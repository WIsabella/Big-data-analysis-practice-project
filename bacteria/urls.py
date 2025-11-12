from django.urls import path
from. import views

urlpatterns = [
    path("search/", views.search_bacteria, name="bacteria_search"),
    path("upload/", views.add_bacteria, name="bacteria_add"),
    path("create_order/", views.createOrder, name="create_order"),
    path("submmit_order/", views.submmitOrder, name="submmit_order")
]