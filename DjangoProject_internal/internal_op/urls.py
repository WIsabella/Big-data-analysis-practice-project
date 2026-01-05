from django.urls import path
from. import views

urlpatterns = [
    path("search/", views.search_bacteria, name="search"),
    path("detail/", views.bacteria_detail, name="detail"),
    path("update/", views.update_data, name="update"),
    path("check_order/", views.check_order, name="check_order"),
    path("update_order/", views.update_order, name="update_order"),
]