from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from.models import Test1
from.forms import BacteriaSearchForm
from datetime import datetime
from django.conf import settings
from django.db import connection
import os
import csv

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
                    # 表头：根据你的模型字段修改
                    writer.writerow(['保藏号', '分类单元', '分离源', '需氧性'])
                    # 数据行：使用模型字段名（如taxonomy对应“分类单元”）
                    for item in results:
                        writer.writerow([
                            item.deposit_number,
                            item.taxonomic_unit,
                            item.isolation_source,
                            item.notes
                        ])

                print(f"[保存提示] 结果已保存至: {file_path}\n")
                results = list(results.values('deposit_number', 'taxonomic_unit', 'isolation_source', 'notes'))

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
    return render(request, "../templates/index.html", context)

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


#@login_required
def authenticated_search(request):
    return search_bacteria(request)
