from django.urls import path
from . import views

urlpatterns = [
    path('save_data/', views.save_data, name='save_data'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('upload_images/', views.upload_images, name='upload_images'),
    path("upload_genomic_information/", views.upload_genomic_information),
]
