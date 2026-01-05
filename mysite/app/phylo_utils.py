from ete3 import Tree, TreeStyle, NodeStyle, TextFace, faces, BarChartFace
import os
import subprocess
def render_phylogenetic_tree(nwk_file_path, output_dir):
    import os
    from ete3 import Tree, TreeStyle, NodeStyle, TextFace

    # 设置无显示环境，避免 Celery / Linux 无 GUI 崩溃
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    # 确保输出目录存在（防御式，强烈推荐）
    os.makedirs(output_dir, exist_ok=True)

    tree = Tree(nwk_file_path, format=1)

    # --------------------
    # 树样式设置
    # --------------------
    ts = TreeStyle()
    ts.mode = "c"                 # circular
    ts.show_branch_length = True
    ts.show_branch_support = True
    ts.rotation = 90
    ts.scale = 100
    ts.show_leaf_name = False
    ts.title.add_face(
        TextFace(os.path.basename(nwk_file_path), fsize=20, bold=True),
        column=0
    )

    ts.scale_length = 0.05
    ts.draw_guiding_lines = True

    # --------------------
    # 叶节点样式
    # --------------------
    for leaf in tree:
        leaf_style = NodeStyle()
        leaf_style["fgcolor"] = "#1f77b4"
        leaf_style["size"] = 6
        leaf_style["vt_line_width"] = 2
        leaf_style["hz_line_width"] = 2
        leaf_style["vt_line_type"] = 0
        leaf_style["hz_line_type"] = 0
        leaf_style["hz_line_color"] = "#1f77b4"
        leaf_style["vt_line_color"] = "#1f77b4"
        leaf.set_style(leaf_style)

        leaf.add_face(
            TextFace(leaf.name, fsize=12, fgcolor="#333333", bold=True),
            column=0,
            position="branch-right"
        )

    # --------------------
    # 内部节点样式
    # --------------------
    for node in tree.traverse():
        if not node.is_leaf():
            node_style = NodeStyle()
            node_style["fgcolor"] = "#555555"
            node_style["size"] = 0
            node_style["vt_line_width"] = 2
            node_style["hz_line_width"] = 2
            node_style["vt_line_color"] = "#555555"
            node_style["hz_line_color"] = "#555555"
            node.set_style(node_style)

            if hasattr(node, "support"):
                node.add_face(
                    TextFace(f"{node.support:.1f}", fsize=10, fgcolor="#aa0000", bold=True),
                    column=0,
                    position="branch-top"
                )

    # --------------------
    # 输出：固定文件名（关键修改点）
    # --------------------
    image_path = os.path.join(output_dir, "tree.png")

    tree.render(
        image_path,
        w=1600,
        h=1600,
        dpi=300,
        units="px",
        tree_style=ts
    )

    return image_path

    
MUSCLE_BIN = "/usr/local/bin/muscle"   # ← 修改为你服务器的 muscle v5 路径
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator
import os

def muscle_distance_matrix(fasta_text, work_dir):
    fasta_path = os.path.join(work_dir, "tmp.fasta")
    aln_path = os.path.join(work_dir, "tmp.aln")

    # 1. 写入 fasta
    with open(fasta_path, "w") as f:
        f.write(fasta_text)

    # 2. MUSCLE v5 做多序列比对
    cmd = f"{MUSCLE_BIN} -align {fasta_path} -output {aln_path}"
    run_cmd(cmd, "MUSCLE Align for Distance")

    # 3. 用 Biopython 计算距离矩阵
    alignment = AlignIO.read(aln_path, "fasta")
    calculator = DistanceCalculator("identity")
    dm = calculator.get_distance(alignment)

    names = dm.names
    matrix = [list(dm[i]) for i in range(len(names))]

    return names, matrix
def pick_top_k_by_muscle(user_entry, db_entries, top_k, work_dir):
    """
    user_entry: (hdr, seq)
    db_entries: [(hdr, seq), ...]
    """

    fasta_lines = []

    # 用户序列 → 强制唯一
    user_hdr = f"user__{user_entry[0]}"
    fasta_lines.append(f">{user_hdr}\n{user_entry[1]}")

    # 数据库序列 → 强制唯一
    for i, (h, s) in enumerate(db_entries):
        db_hdr = f"db__{h}__{i}"
        fasta_lines.append(f">{db_hdr}\n{s}")

    fasta = "\n".join(fasta_lines) + "\n"

    names, matrix = muscle_distance_matrix(fasta, work_dir)

    user_idx = 0
    distances = []
    for i in range(1, len(names)):
        distances.append((matrix[user_idx][i], names[i]))

    distances.sort(key=lambda x: x[0])
    selected_names = {name for _, name in distances[:top_k]}

    # 映射回原始 db_entries
    result = []
    for i, (h, s) in enumerate(db_entries):
        if f"db__{h}__{i}" in selected_names:
            result.append((h, s))

    return result

def run_cmd(cmd, step_name):
    print(f"Executing {step_name} command: {cmd}")
    subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    print(f"{step_name} completed successfully.")
    
# 简单 FASTA 解析器：把输入拆成 [(header, seq), ...]
def parse_fasta_text(fasta_text):
    fasta_text = fasta_text.replace("\r", "")
    lines = fasta_text.splitlines()
    entries = []
    header = None
    seq_chunks = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header:
                entries.append((header, "".join(seq_chunks)))
            header = line[1:].strip()
            seq_chunks = []
        else:
            seq_chunks.append(line)
    if header:
        entries.append((header, "".join(seq_chunks)))
    return entries
    
def wrap_sequence(seq, line_width=60):
    """
    将序列按固定行宽换行
    """
    return "\n".join(seq[i:i + line_width] for i in range(0, len(seq), line_width))


def normalize_fasta_entries(entries, line_width=60, single_line_threshold=120):
    """
    entries: [(header, seq), ...]
    自动识别超长单行序列并换行
    返回修正后的 FASTA 文本
    """
    fasta_blocks = []

    for header, seq in entries:
        # 清理空格/换行并统一大写
        seq = seq.replace(" ", "").replace("\n", "").upper()
        # 超长序列换行
        if len(seq) >= single_line_threshold:
            seq = wrap_sequence(seq, line_width)
        fasta_blocks.append(f">{header}\n{seq}")

    return "\n".join(fasta_blocks)
    
def package_nwk_files(task_ids, zip_path):
    """将多个任务的 nwk 文件打包成一个 zip"""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for task_id in task_ids:
            task_dir = os.path.join(settings.MEDIA_ROOT, "phylogeny_tasks", task_id)
            nwk_file = os.path.join(task_dir, "output_tree.nwk")
            if os.path.exists(nwk_file):
                zipf.write(nwk_file, arcname=f"{task_id}.nwk")
    return zip_path