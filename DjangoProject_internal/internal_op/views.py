from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from .models import Test1
from .forms import BacteriaSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from external_db_models.models import Order
from django.views.decorators.csrf import csrf_exempt
    
'''内部人员操作，实现更高级功能'''
'''搜索'''
# 辅助函数
def search_bacteria_helper(search_conditions, page, per_page=15):
    queryset = Test1.objects.all()
    if search_conditions.get('taxonomic_unit'):
        queryset = queryset.filter(taxonomic_unit__icontains=search_conditions['taxonomic_unit'])
    if search_conditions.get('health_status'):
        queryset = queryset.filter(health_status__icontains=search_conditions['health_status'])

    total_count = queryset.count()

    paginator = Paginator(queryset, per_page)
    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    columns_list = ['deposit_number', 'closest_species', 'taxonomic_unit', 'isolation_source']
    results = list(paginated_results.object_list.values(*columns_list))

    return {
        "results": results,
        "total_count": total_count,
        "current_page": paginated_results.number,
        "total_pages": paginator.num_pages
    }

@api_view(['POST'])
def search_bacteria(request):
    response_data = {
        "success": False,
        "message": "",
        "total_count": 0,
        "current_page": 1,
        "total_pages": 0,
        "results": []
    }
    per_page = 15

    params = request.data if hasattr(request, 'data') else request.POST
    page = int(params.get('page', 1))
    new_search = params.get('new_search', False)

    # 场景1：新搜索（new_search=True）
    if new_search:
        form = BacteriaSearchForm(params)
        if form.is_valid():
            search_conditions = {
                'taxonomic_unit': form.cleaned_data.get('taxonomic_unit', '').strip(),
                'health_status': form.cleaned_data.get('health_status', '').strip()
            }
            print(
                f"[新搜索] 条件: {search_conditions['taxonomic_unit'] or '空'}/"
                f"{search_conditions['health_status'] or '空'}, 页码: {page}"
            )

            search_result = search_bacteria_helper(search_conditions, page, per_page)

            request.session['search_conditions'] = search_conditions
            request.session['search_columns'] = ['deposit_number', 'closest_species', 'taxonomic_unit', 'isolation_source']

            response_data.update({
                "success": True,
                "message": "查询成功",
                **search_result  # 解包辅助函数返回的结果
            })
        else:
            response_data["message"] = f"搜索参数非法：{form.errors}"

    # 场景2：翻页（new_search=False）
    else:
        if 'search_conditions' in request.session:
            # 从Session读取缓存的搜索条件
            search_conditions = request.session['search_conditions']
            print(f"[翻页] 复用条件: {search_conditions}, 页码: {page}")

            search_result = search_bacteria_helper(search_conditions, page, per_page)

            response_data.update({
                "success": True,
                "message": "查询成功",
                **search_result
            })
        else:
            response_data["message"] = "请先执行搜索"

    return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})

'''查看详情视图'''
@api_view(['GET', 'POST'])
def bacteria_detail(request):
    # 获取前端传递的id参数
    deposit_number = request.data.get('deposit_number')
    if not deposit_number:
        return JsonResponse({
            'success': False,
            'message': 'error'
        })
    try:
        bacteria = Test1.objects.get(deposit_number=deposit_number)
    except Test1.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '未找到对应数据'
        })

    detail_data = {
        'deposit_number': bacteria.deposit_number,#保藏号
        'isolation_date': bacteria.isolation_date,#分离日期
        'isolator': bacteria.isolator,#分离人
        'original_strain_number': bacteria.original_strain_number,#原始菌株编号
        'closest_species': bacteria.closest_species,#物种名（拉丁学名）
        'similarity_percentage': bacteria.similarity_percentage,#相似度
        'number_16s': bacteria.number_16s,
        'length': bacteria.length,
        'accession': bacteria.accession,
        'taxonomic_unit': bacteria.taxonomic_unit,#分类单元
        'isolation_source': bacteria.isolation_source,#来源信息
        'sample_collection_time':bacteria.sample_collection_time,#样品采集时间
        'gender': bacteria.gender,#性别
        'age': bacteria.age,#年龄
        'health_status': bacteria.health_status,#健康状况
        'living_area': bacteria.living_area,#生活地区
        'bmi': bacteria.bmi,
        'isolation_medium':bacteria.isolation_medium,#分离培养基
        'identification_medium':bacteria.identification_medium,#鉴定培养基
        'culture_temperature':bacteria.culture_temperature,#培养温度
        'recommended_culture_time':bacteria.recommended_culture_time,#建议培养时间
        'aerobicity':bacteria.aerobicity,#需氧性
        'receipt_date':bacteria.receipt_date,#接收日期
        'slant_photo':bacteria.slant_photo,#斜面照片
        'liquid_photo':bacteria.liquid_photo,#液体照片
        'slant_storage':bacteria.slant_storage,#斜面上架
        'glycerol_preservation':bacteria.glycerol_preservation,#甘油保种
        'lyophilization_preservation':bacteria.lyophilization_preservation,#冷干保种
        'notes': bacteria.notes,  # 备注
        'metabolomics_data': bacteria.metabolomics_data,#代谢组学数据
        'genomic_information': bacteria.genomic_information#基因组学数据
    }

    return JsonResponse({
        'success': True,
        'detail': detail_data
    })

@api_view(['POST'])
def update_data(request):
    data=request.data
    deposit_number = data.get('deposit_number')

    try:
        bacteria = Test1.objects.get(deposit_number=deposit_number)
    except Test1.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message':"not found"
        })
        
    data.pop("deposit_number")
    
    for field,value in data.items():
        if hasattr(bacteria,field):
            setattr(bacteria,field,value)
        else:
            print(f"无效字段'{field}',已跳过")
    try:
        bacteria.save()
    except ValueError as e:
        return JsonResponse({
            'success':False,
            'message':str(e)
        })
        
    return JsonResponse({
        'success': True,
        'message':"valid modify"
    })

@api_view(['POST'])
def check_order(request):
    filter_status = request.data.get('filter')

    if not filter_status:
        queryset  = Order.objects.all()
    elif filter_status == "finished_only":
        queryset  = Order.objects.filter(order_status="已完成")
    elif filter_status == "ongoing_only":
        queryset  = Order.objects.filter(order_status="未完成")
    else:
        queryset = Order.objects.all()

    page=request.data.get('page')
    paginator = Paginator(queryset, 10)
    try:
        paginated_orders = paginator.page(page)
    except PageNotAnInteger:
        paginated_orders = paginator.page(1)
    except EmptyPage:
        paginated_orders = paginator.page(paginator.num_pages)

    orders_list = list(paginated_orders.object_list.values())
    return JsonResponse({
        "success": True,#成功
        "count":paginator.count,#总数
        "total_pages": paginator.num_pages,#总页数
        "current_page": paginated_orders.number,#当前页码
        "results":orders_list#结果字典列表
    })


@api_view(['POST'])
def update_order(request):
    response_data={
        "success":False,
        "message":""
    }
    try: 
        order=Order.objects.get(order_id=request.data.get('order_id'))
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message':"not found"
        })
        
    new_status=request.data.get('new_status')
    
    if not new_status:
        response_data["message"]="无效的修改"
        return JsonResponse(response_data)
        
    order.order_status=new_status
    order.save()
    response_data["success"]=True
    response_data["message"]="修改成功"
    return JsonResponse(response_data)
