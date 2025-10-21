from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from.models import Test1
from.forms import BacteriaSearchForm
from datetime import datetime
from django.conf import settings
from django.db import connection
import os
import csv
import pandas as pd

'''定义权限，每个用户可以拥有哪一些权限'''

'''查询权限'''
class CanQueryBacteria(BasePermission):
    def has_permission(self,request, view):
        return request.user.has_perm("bacteria.view_test1")

'''上传权限'''
class CanAddBacteria(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("bacteria.add_test1")

'''删除权限'''
class CanDeleteBacteria(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('bacteria.delete_test1')

def HomePage(request):
    return render(request, '../templates/index.html')
@api_view(['GET'])
def search_bacteria(request):
    '''测试新功能'''
    form = BacteriaSearchForm(request.GET or None)
    results = []
    is_authenticated = request.user.is_authenticated

    if form.is_valid() and request.GET:
        taxonomy_value = form.cleaned_data.get('taxonomic_unit')

        if taxonomy_value:
            # 1. 直接使用ORM查询，Django会自动处理特殊字符转义
            # 无需手动调用escape_string，避免AttributeError
            results = Test1.objects.filter(taxonomic_unit__icontains=taxonomy_value)
            # 2. 终端提示
            print(f"\n[查询提示] 关键词: {taxonomy_value}，查询到 {len(results)} 条结果")

            # 3. 保存结果到本地（同上）
            if results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"{timestamp}_query_results.csv"
                file_path = os.path.join(os.getcwd(), filename)

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    item_values = []
                    columns_list = []
                    # 表头：根据你的模型字段修改
                    if not is_authenticated:
                       columns_list.extend(['deposit_number', 'taxonomic_unit', 'isolation_source', 'notes'])
                       writer.writerow(['保藏号', '分类单元', '分离源', '需氧性'])
                       for item in results:
                           item_values.append([
                               item.deposit_number,
                               item.taxonomic_unit,
                               item.isolation_source,
                               item.notes
                           ])

                    elif is_authenticated and request.user.role == 'student':
                        columns_list.extend(['deposit_number', 'taxonomic_unit', 'isolation_source', 'notes', 'health_status'])
                        writer.writerow(['保藏号', '分类单元', '分离源', '需氧性', '健康状况'])
                        for item in results:
                            item_values.append([
                                item.deposit_number,
                                item.taxonomic_unit,
                                item.isolation_source,
                                item.notes,
                                item.health_status
                            ])
                    # 数据行：使用模型字段名（如taxonomy对应“分类单元”）
                    elif is_authenticated and request.user.role == 'admin':
                        columns_list.extend(['deposit_number', 'taxonomic_unit', 'isolation_source', 'notes', 'health_status', 'living_area'])
                        writer.writerow(['保藏号', '分类单元', '分离源', '需氧性', '健康状况', '生活地区'])
                    for item in results:
                        item_values.append([
                            item.deposit_number,
                            item.taxonomic_unit,
                            item.isolation_source,
                            item.notes,
                            item.health_status,
                            item.living_area
                        ])
                    writer.writerows(item_values)

                print(f"[保存提示] 结果已保存至: {file_path}\n")
                results = list(results.values(*columns_list))

                return JsonResponse({'results': results})
            else:
                print("[查询提示] 未查询到匹配结果\n")
        else:
            results = []
            print("[查询提示] 搜索关键词为空\n")

    context = {
        "form": form,
        "results": results,
        "is_authenticated": is_authenticated,
    }
    return JsonResponse(context)

    '''原始逻辑'''

    # form = BacteriaSearchForm(request.GET or None)
    # results = []
    # is_authenticated = request.user.is_authenticated
    #
    # if form.is_valid() and request.GET:
    #     query_params = {
    #         field: value
    #         for field, value in form.cleaned_data.items()
    #         if value
    #     }
    #
    #     if query_params:
    #         query_filter = {}
    #         for field, value in query_params.items():
    #             if field == "Closest_species":
    #                 query_filter[f"{field}__icontains"] = value
    #             else:
    #                 query_filter[f"{field}__icontains"] = value
    #
    #         results = Test1.objects.filter(**query_filter)
    #     else:
    #         results = []
    #
    # context = {
    #     "form": form,
    #     "results": results,
    #     "is_authenticated": is_authenticated,
    # }
    # return render(request, "../templates/index.html", context)


'''实现用户的登录功能'''
@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAddBacteria])
def add_bacteria(request):
   try:
    bacteria_list = []
    excel_file = request.FILES.get('excel_file')
    data = pd.read_excel(excel_file)

    for index in data.index:
        values = data.loc[index, :].to_dict()
        bacteria_list.append(
           Test1(**values)
        )
    Test1.objects.bulk_create(bacteria_list)
    return Response({"message": "Bacteria added successfully!"}, status=201)
   except Exception as e:
       return Response({"message": str(e)}, status=400)