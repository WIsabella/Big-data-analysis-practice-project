import os
import shutil
from celery import shared_task
from django.conf import settings
import subprocess
from .phylo_utils import render_phylogenetic_tree, pick_top_k_by_muscle,run_cmd,parse_fasta_text,wrap_sequence
from datetime import datetime, timedelta
import glob

MAX_DB_COMPARE = 30  # 测试环境最多读取 30 条数据库序列

@shared_task(bind=True)
def build_phylogenetic_tree_task(self, fasta_data, task_id, use_db_flag=False, top_k=None):
    """
    构建系统/用户序列的进化树
    - fasta_data: 用户上传或粘贴的 FASTA 文本
    - task_id: 当前任务 ID
    - use_db_flag: 是否使用数据库序列
    - top_k: 每条用户序列匹配的数据库序列数量
    """
    task_dir = os.path.join(settings.MEDIA_ROOT, "phylogeny_tasks", task_id)
    os.makedirs(task_dir, exist_ok=True)

    input_fasta_path = os.path.join(task_dir, "input.fasta")
    output_tree_nwk = os.path.join(task_dir, "output_tree.nwk")

    try:
        # 写入用户原始序列
        with open(input_fasta_path, "w") as f:
            f.write(fasta_data)

        user_entries = parse_fasta_text(fasta_data)

        # ---------- 加载数据库 ----------
        db_entries = []
        if use_db_flag and top_k:
            from .models import Test1
            for row in Test1.objects.only("deposit_number", "number_16s").iterator():
                seq = (row.number_16s or "").strip().upper()
                if len(seq) >= 50:
                    db_entries.append((row.deposit_number, seq))
                if len(db_entries) >= MAX_DB_COMPARE:
                    break

        # ---------- 为每条用户序列选 top_k ----------
        selected_db = set()
        if use_db_flag and top_k and db_entries:
            for hdr, seq in user_entries:
                picked = pick_top_k_by_muscle(
                    (hdr, seq),
                    db_entries,
                    top_k,
                    task_dir
                )
                selected_db.update(picked)

        # ---------- 合并最终序列 (保持所有用户序列，防止覆盖) ----------
        final_entries = []
        # 先加用户序列
        for hdr, seq in user_entries:
            final_entries.append((hdr, seq))
        # 再加数据库序列
        for hdr, seq in selected_db:
            final_entries.append((hdr, seq))

        # ---------- FASTA 拼接，自动换行 ----------
        final_fasta = "".join(
            f">{hdr}\n{wrap_sequence(seq)}\n" for hdr, seq in final_entries
        )

        final_fasta_path = os.path.join(task_dir, "final.fasta")
        with open(final_fasta_path, "w") as f:
            f.write(final_fasta)

        # ---------- 构建树 ----------
        aligned = os.path.join(task_dir, "aligned.fasta")
        trimmed = os.path.join(task_dir, "trimmed.fasta")

        run_cmd(f"muscle -align {final_fasta_path} -output {aligned}", "MUSCLE")
        run_cmd(f"trimal -in {aligned} -out {trimmed} -automated1", "trimAl")
        run_cmd(f"FastTree -nt -gtr {trimmed} > {output_tree_nwk}", "FastTree")

        tree_png = render_phylogenetic_tree(output_tree_nwk, task_dir)
        
        for f in glob.glob(os.path.join(task_dir, "*.fasta")) + glob.glob(os.path.join(task_dir, "*.aligned")):
            if f not in [output_tree_nwk]:
                try:
                    os.remove(f)
                except:
                    pass
        return {
            "status": "SUCCESS",
            "message": "已完成",
            "img_url": f"/img/phylogeny_tasks/{task_id}/{os.path.basename(tree_png)}",
            "file": f"/media/phylogeny_tasks/{task_id}/output_tree.nwk"
        }

    except Exception as e:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise e

def cleanup_old_phylogeny_tasks(days=7):
    base_dir = os.path.join(settings.MEDIA_ROOT, "phylogeny_tasks")
    cutoff_time = datetime.now() - timedelta(days=days)

    for task_id in os.listdir(base_dir):
        task_path = os.path.join(base_dir, task_id)
        if not os.path.isdir(task_path):
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(task_path))
        if mtime < cutoff_time:
            shutil.rmtree(task_path, ignore_errors=True)