# views.py
import os
import json
import traceback
from datetime import datetime
from io import BytesIO, StringIO
import csv
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from openpyxl import load_workbook
from PIL import Image
from .models import Test1
from .phylo_utils import render_phylogenetic_tree,parse_fasta_text,normalize_fasta_entries,wrap_sequence,package_nwk_files

def parse_date(value, fmt_list=None):
    if not value:
        return None
    value = value.strip()
    if not fmt_list:
        # 默认支持多种常见格式
        fmt_list = ("%Y-%m-%dT%H:%M", "%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d")
    for fmt in fmt_list:
        try:
            return datetime.strptime(value, fmt)
        except:
            continue
    return None

def safe_int(value):
    try:
        return int(value)
    except:
        return None

def safe_float(value):
    try:
        return float(value)
    except:
        return None

def safe_str(value):
    try:
        return str(value).strip()
    except:
        return ""
        
# 自动生成保藏号
def generate_deposit_number():
    last = Test1.objects.order_by('-deposit_number').first()
    if last and last.deposit_number:
        prefix = last.deposit_number[:2]
        number = int(last.deposit_number[2:])
        number += 1
        if number > 9999:
            c1, c2 = prefix
            if c2 < 'Z':
                c2 = chr(ord(c2) + 1)
            elif c1 < 'Z':
                c1 = chr(ord(c1) + 1)
                c2 = 'A'
            else:
                c1, c2 = 'A', 'A'
            prefix = c1 + c2
            number = 0
        return f"{prefix}{number:04d}"
    else:
        return "HA0200"
#        
def handle_uploaded_file(file_obj, subfolder="uploads", new_name=None):

    if not file_obj:
        return "未上传"

    ext = os.path.splitext(file_obj.name)[1]
    if new_name:
        filename = f"{new_name}{ext}"
    else:
        filename = file_obj.name

    save_path = os.path.join(subfolder, filename)
    path = default_storage.save(save_path, ContentFile(file_obj.read()))
    return path

@csrf_exempt
def save_data(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method!"}, status=405)

    try:
        
        raw_text_data = request.POST.get("text_data")  # 获取 text_data
        files = request.FILES
        results = []

        try:
            data = json.loads(raw_text_data) if raw_text_data else {}
        except Exception as e:
            print("JSON parse error:", e)
            data = {}

        # 字段解析
        sample_collection_time = parse_date(data.get("sample_collection_time"))
        receipt_date = parse_date(data.get("receipt_date"))
        similarity_percentage = safe_float(data.get("similarity_percetage"))
        age = safe_int(data.get("age"))
        BMI = safe_float(data.get("BMI"))
        culture_temperature = safe_int(data.get("culture_temperature"))
        slant_storage = safe_int(data.get("slant_storage"))
        glycerol_preservation = safe_int(data.get("glycerol_preservation"))
        lyophilization_preservation = safe_int(data.get("lyophilization_preservation"))
        length = safe_int(data.get("length"))

        deposit_number = generate_deposit_number()

        # 创建记录
        # 先创建记录，拿到主键
        new_data = Test1.objects.create(
            deposit_number=deposit_number,
            isolation_date=data.get('isolation_date'),
            isolator=data.get('isolator'),
            original_strain_number=data.get('origin_strain_number'),
            closest_species=data.get('closest_species'),
            similarity_percentage=similarity_percentage,
            number_16s=data.get('_16s'),
            length=length,
            accession=data.get('accession'),
            taxonomic_unit=data.get('taxonomic_unit'),
            isolation_source=data.get('isolation_source'),
            sample_collection_time=sample_collection_time,
            gender=data.get('gender'),
            age=age,
            health_status=data.get('health_status'),
            living_area=data.get('living_area'),
            bmi=BMI,
            isolation_medium=data.get('isolation_medium'),
            identification_medium=data.get('identification_medium'),
            culture_temperature=culture_temperature,
            recommended_culture_time=safe_int(data.get('recommended_culture_time')),
            aerobicity=data.get('aerobicity'),
            receipt_date=receipt_date,
            notes=data.get('notes'),
            metabolomics_data="",
            Genomic_Information=""
        )

# 安全处理图片
        slant_file = files.get("slant_photo")
        liquid_file = files.get("liquid_photo")

        slant_photo_path = handle_uploaded_file(slant_file, new_name=f"{new_data.pk}_slant") if slant_file else "未上传"
        liquid_photo_path = handle_uploaded_file(liquid_file, new_name=f"{new_data.pk}_liquid") if liquid_file else "未上传"

# 更新数据库字段
        new_data.slant_photo = slant_photo_path
        new_data.liquid_photo = liquid_photo_path
        new_data.save()
        
        results.append(deposit_number)

        return JsonResponse({"success": True, "message": "Data saved!", "deposit_numbers": results}, status=200)

    except Exception as e:
        print("❌ Error:", e)
        return JsonResponse({"success": False, "message": str(e)}, status=400)





ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_SAVE_DIR = "uploads"  # media 下目录

def save_image_by_deposit_number(pil_img, deposit_number, img_type):
    """按主键保存图片，返回相对路径"""
    pil_img = pil_img.convert("RGB")
    img_byte_arr = BytesIO()
    pil_img.save(img_byte_arr, format="JPEG", quality=95)
    if img_byte_arr.tell() > MAX_IMAGE_SIZE:
        raise ValueError(f"图片大小超过限制 {MAX_IMAGE_SIZE//1024//1024}MB")

    filename = f"{deposit_number}_{img_type}.jpg"
    save_dir = os.path.join(settings.MEDIA_ROOT, IMAGE_SAVE_DIR)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as f:
        img_byte_arr.seek(0)
        f.write(img_byte_arr.read())

    return os.path.join(IMAGE_SAVE_DIR, filename)


@csrf_exempt
def upload_images(request):
    """
    POST 上传图片（slant / liquid 可选填）
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "只允许 POST"}, status=405)

    deposit_number = request.POST.get("deposit_number", "").strip()
    if not deposit_number:
        return JsonResponse({"success": False, "message": "缺少 deposit_number"}, status=400)

    slant_file = request.FILES.get("slant_photo")
    liquid_file = request.FILES.get("liquid_photo")

    if not slant_file and not liquid_file:
        return JsonResponse({"success": False, "message": "未上传图片"}, status=400)

    result = {}
    result_paths = {}
    try:
        obj = Test1.objects.filter(deposit_number=deposit_number).first()
        if not obj:
            return JsonResponse({"success": False, "message": "未找到对应主键的记录"}, status=404)
            
        if slant_file:
            pil_img = Image.open(slant_file)
            path = save_image_by_deposit_number(pil_img, deposit_number, "slant")
            obj.slant_photo = path
            result["slant_photo"] = path

        if liquid_file:
            pil_img = Image.open(liquid_file)
            path = save_image_by_deposit_number(pil_img, deposit_number, "liquid")
            obj.liquid_photo = path
            result["liquid_photo"] = path
        obj.save()
        # 返回你要求的格式
        return JsonResponse({
            "success": True,
            "message": "上传成功",
            "paths": result
        })

    except Exception as e:
        print("ERROR:", repr(e))
        return JsonResponse({"success": False,"message": str(e)}, status=500)

@csrf_exempt
def import_csv(request):
    import traceback  
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只允许 POST'}, status=405)

    if 'File' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': '未接收到文件'}, status=400)

    File = request.FILES['File']
    file_name = File.name.lower()

    try:
        
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(File, engine='openpyxl')
        else:
            file_bytes = File.read()
            try:
                csv_str = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                csv_str = file_bytes.decode('gb2312', errors='ignore')
            df = pd.read_csv(StringIO(csv_str))

        # 确保至少有 31 列
        while df.shape[1] < 31:
            df[df.shape[1]] = ""

        created_count = 0
        skipped_count = 0
        error_rows = []

        # 从第 1 行开始迭代，跳过表头
        for idx, row in df.iterrows():
            row = list(row) + [""] * (31 - len(row))  # 补齐列
            try:
                # 如果第一列是 'deposit_number' 或者空，则跳过（避免导入表头）
                first_cell = safe_str(row[0]).lower()
                if first_cell in ("deposit_number", ""):
                    skipped_count += 1
                    continue

                # 日期字段
                sample_collection_time = parse_date(row[11])
                receipt_date = parse_date(row[22])

                # 布尔字段
                glycerol_preservation = safe_str(row[26]).lower() == '是'
                lyophilization_preservation = safe_str(row[27]).lower() == '是'

                # 数值字段
                similarity_percentage = safe_float(row[5])
                length = safe_int(row[7])
                age = safe_int(row[13])
                bmi = safe_float(row[16])
                culture_temperature = safe_int(row[19])
                recommended_culture_time = safe_int(row[20])
                slant_storage = safe_int(row[25])

                # 创建记录
                Test1.objects.create(
                    deposit_number=safe_str(row[0]),
                    isolation_date=safe_str(row[1]),
                    isolator=safe_str(row[2]),
                    original_strain_number=safe_str(row[3]),
                    closest_species=safe_str(row[4]),
                    similarity_percentage=similarity_percentage,
                    number_16s=safe_str(row[6]),
                    length=length,
                    accession=safe_str(row[8]),
                    taxonomic_unit=safe_str(row[9]),
                    isolation_source=safe_str(row[10]),
                    sample_collection_time=sample_collection_time,
                    gender=safe_str(row[12]),
                    age=age,
                    health_status=safe_str(row[14]),
                    living_area=safe_str(row[15]),
                    bmi=bmi,
                    isolation_medium=safe_str(row[17]),
                    identification_medium=safe_str(row[18]),
                    culture_temperature=culture_temperature,
                    recommended_culture_time=recommended_culture_time,
                    aerobicity=safe_str(row[21]),
                    receipt_date=receipt_date,
                    slant_photo=None,
                    liquid_photo=None,
                    slant_storage=slant_storage,
                    glycerol_preservation=glycerol_preservation,
                    lyophilization_preservation=lyophilization_preservation,
                    notes=safe_str(row[28]),
                    metabolomics_data=safe_str(row[29]),
                    Genomic_Information=safe_str(row[30])
                )
                created_count += 1

            except Exception as e:
                skipped_count += 1
                error_info = {
                    'row': idx + 2,  # header + 0-index
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                error_rows.append(error_info)
                print(f"第{idx+2}行导入失败：{e}")
                print(traceback.format_exc())

        return JsonResponse({
            'status': 'success',
            'message': f'导入完成，创建 {created_count} 条，跳过 {skipped_count} 条',
            'created_count': created_count,
            'skipped_count': skipped_count,
            'error_rows': error_rows
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
        
@csrf_exempt
def upload_genomic_information(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "只允许 POST"}, status=405)

    deposit_number = request.POST.get("deposit_number", "").strip()
    fasta_file = request.FILES.get("genomic_file")

    if not deposit_number:
        return JsonResponse({"success": False, "message": "缺少 deposit_number"}, status=400)

    if not fasta_file:
        return JsonResponse({"success": False, "message": "未上传 fasta 文件"}, status=400)

    try:
        obj = Test1.objects.filter(deposit_number=deposit_number).first()
        if not obj:
            return JsonResponse({"success": False, "message": "未找到对应保藏号"}, status=404)

        # --------- 存储位置设置 ---------
        subfolder = "Genomic_Information"    # media/Genomic_Information/
        os.makedirs(os.path.join(settings.MEDIA_ROOT, subfolder), exist_ok=True)

        # --------- 修改文件名 ---------
        new_name = f"{deposit_number}_Genomic"
        ext = os.path.splitext(fasta_file.name)[1]
        filename = f"{new_name}{ext}"

        save_path = os.path.join(subfolder, filename)
        stored_path = default_storage.save(save_path, ContentFile(fasta_file.read()))

        obj.Genomic_Information = stored_path
        obj.save()

        return JsonResponse({
            "success": True,
            "message": "基因组文件上传成功",
            "deposit_number": deposit_number,
            "file_path": stored_path
        }, status=200)

    except Exception as e:
        print("❌ Genomic Upload Error:", e)
        return JsonResponse({"success": False, "message": str(e)}, status=500)

from celery.result import AsyncResult
@csrf_exempt
def query_task_status(request, task_celery_id):
    """根据 Celery ID 查询任务状态"""
    
    task = AsyncResult(task_celery_id)
    
    response_data = {
        'state': task.state,
        'status_message': '任务正在处理中...'
    }
    
    if task.state == 'SUCCESS':
        # 任务成功，返回结果 (这是 tasks.py 中 return 的内容)
        response_data['status_message'] = '任务完成！'
        response_data['result'] = task.result
        
    elif task.state == 'FAILURE':
        # 任务失败，返回错误信息
        response_data['status_message'] = '任务失败！'
        response_data['error'] = str(task.result) # Celery 会在 result 存储异常
        
    return JsonResponse(response_data)

import os
import json
import uuid
import re
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Test1
from .tasks import build_phylogenetic_tree_task
import difflib
# 合法碱基（IUPAC 常见符号，含 N、U 等）
IUPAC_BASES = set(list("ACGTURYKMSWBDHVN-."))  # include gap '.' '-' and ambiguous letters



def validate_sequence_chars(seq):
    seq = seq.upper()
    for ch in seq:
        if ch not in IUPAC_BASES:
            return False, ch
    return True, None

TOP_K_CLOSEST = 10       # 选出与用户序列最相似的10条去构建进化树
import subprocess
import tempfile
import os

MUSCLE_BIN = "/usr/local/bin/muscle"   # ← 修改为你服务器的 muscle v5 路径

@csrf_exempt
def submit_sequences_with_db(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "只允许 POST"}, status=405)

    # =========================================================
    # 1. 获取用户上传 / 粘贴序列
    # =========================================================
    all_entries = []  # 所有序列，用于 whole=true

    # ---------- 上传文件 ----------
    for f in request.FILES.getlist("fasta_files"):
        try:
            text = f.read().decode("utf-8")
            parsed = parse_fasta_text(text)
            if parsed:
                all_entries.extend(parsed)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"读取上传文件失败: {e}"},
                status=400
            )

    # ---------- 多个粘贴框 ----------
    pasted_texts = request.POST.getlist("pasted_sequences")
    for idx, pasted_text in enumerate(pasted_texts):
        pasted_text = pasted_text.strip()
        if not pasted_text:
            continue

        parsed = parse_fasta_text(pasted_text)
        if parsed:
            all_entries.extend(parsed)
        else:
            # 裸序列兜底
            seq = pasted_text.replace("\n", "").replace(" ", "").upper()
            ok, bad = validate_sequence_chars(seq)
            if not ok:
                return JsonResponse(
                    {"status": "error", "message": f"非法字符: {bad}"},
                    status=400
                )
            all_entries.append((f"user_seq_{idx+1}", seq))

    # ---------- 购物车序列 ----------
    cart_ids = []
    try:
        cart_ids = json.loads(request.POST.get("cart_ids", "[]"))
        if not isinstance(cart_ids, list):
            cart_ids = []
    except:
        cart_ids = []

    if cart_ids:
        qs = Test1.objects.filter(deposit_number__in=cart_ids).only("deposit_number", "number_16s")
        for row in qs:
            seq = (row.number_16s or "").strip().replace("\r", "").replace("\n", "").replace(" ", "").upper()
            if len(seq) < 50:
                continue
            ok, _ = validate_sequence_chars(seq)
            if ok:
                all_entries.append((row.deposit_number, seq))

    if not all_entries:
        return JsonResponse({"status": "error", "message": "没有有效序列可比对"}, status=400)

    # =========================================================
    # 2. 解析参数
    # =========================================================
    use_db_flag = request.POST.get("use_db", "false").lower() == "true"
    TOP_K = int(request.POST.get("top_k", 5)) if use_db_flag else None
    whole_flag = request.POST.get("whole", "true").lower() == "true"
    if not use_db_flag:
        whole_flag = True

    # =========================================================
    # 3. whole=true
    # =========================================================
    if whole_flag:
        cleaned = []
        for hdr, seq in all_entries:
            seq_clean = seq.replace(" ", "").replace("\n", "").upper()
            ok, _ = validate_sequence_chars(seq_clean)
            if ok and len(seq_clean) >= 50:
                cleaned.append((hdr, seq_clean))

        if not cleaned:
            return JsonResponse({"status": "error", "message": "没有有效序列可比对"}, status=400)

        final_fasta_text = normalize_fasta_entries(cleaned)
        task_id = str(uuid.uuid4())
        task_result = build_phylogenetic_tree_task.delay(
            final_fasta_text, task_id, use_db_flag, TOP_K
        )

        return JsonResponse({
            "status": "submitted",
            "mode": "whole",
            "task_public_id": task_id,
            "task_celery_id": task_result.id
        }, status=202)

    # =========================================================
    # 4. whole=false: 每条序列单独任务（方案B）
    # =========================================================
    tasks = []
    for hdr, seq in all_entries:
        seq_clean = seq.replace(" ", "").replace("\n", "").upper()
        ok, _ = validate_sequence_chars(seq_clean)
        if not ok or len(seq_clean) < 50:
            continue

        single_fasta = normalize_fasta_entries([(hdr, seq_clean)])
        task_id = str(uuid.uuid4())
        task_result = build_phylogenetic_tree_task.delay(
            single_fasta, task_id, use_db_flag, TOP_K
        )

        tasks.append({
            "headers": [hdr],
            "task_public_id": task_id,
            "task_celery_id": task_result.id
        })

    if not tasks:
        return JsonResponse({"status": "error", "message": "没有有效序列可提交任务"}, status=400)

    return JsonResponse({"status": "submitted", "mode": "split", "tasks": tasks}, status=202)

    
@csrf_exempt
def query_split_tasks(request):
    """
    split 模式聚合查询（支持 FormData 或 JSON）
    """
    import json
    import os
    import zipfile
    from datetime import datetime
    from django.conf import settings
    from django.http import JsonResponse
    from celery.result import AsyncResult

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "只支持 POST 方法"}, status=405)

    # -------------------- 解析 tasks --------------------
    tasks = []
    if "tasks" in request.POST:
        try:
            tasks = json.loads(request.POST["tasks"])
        except Exception as e:
            return JsonResponse({"status": "error", "message": "tasks 参数解析失败", "error": str(e)}, status=400)
    else:
        try:
            data = json.loads(request.body)
            tasks = data.get("tasks", [])
        except:
            return JsonResponse({"status": "error", "message": "tasks 参数缺失"}, status=400)

    if not isinstance(tasks, list):
        return JsonResponse({"status": "error", "message": "tasks 必须是列表"}, status=400)

    images = []
    nwk_files = []

    # -------------------- 检查任务状态 --------------------
    for t in tasks:
        celery_id = t.get("task_celery_id")
        if not celery_id:
            return JsonResponse({"status": "error", "message": "每个任务必须包含 task_celery_id"}, status=400)
        task = AsyncResult(celery_id)

        if task.state == "SUCCESS":
            images.append(task.result.get("img_url"))
            nwk_files.append({
                "file": task.result.get("file"),
                "headers": t.get("headers", [t.get("task_celery_id")])
            })
        elif task.state == "FAILURE":
            return JsonResponse({
                "status": "error",
                "message": f"任务 {celery_id} 失败",
                "error": str(task.result)
            }, status=500)
        else:
            return JsonResponse({
                "status": "pending",
                "message": f"任务 {celery_id} 仍在处理中"
            }, status=202)

    # -------------------- 打包 nwk 文件 --------------------
    zip_name = f"phylo_split_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_dir = os.path.join(settings.MEDIA_ROOT, "phylogeny_tasks")
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for t_file in nwk_files:
            f = t_file["file"]
            headers = t_file["headers"]
            # 替换 MEDIA_URL 为 MEDIA_ROOT
            if f.startswith(settings.MEDIA_URL):
                real_path = os.path.join(settings.MEDIA_ROOT, f[len(settings.MEDIA_URL):])
            else:
                real_path = f  # 保底

            if os.path.exists(real_path):
                # 使用 headers 列表生成唯一文件名
                safe_name = "_".join([h.replace(">", "").replace("/", "_") for h in headers])
                arcname = f"{safe_name}_output_tree.nwk"
                zipf.write(real_path, arcname=arcname)

    return JsonResponse({
        "status": "SUCCESS",
        "images": images,
        "zip_file": f"/img/phylogeny_tasks/{zip_name}"
    })



