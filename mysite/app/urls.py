# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('save_data/', views.save_data, name='save_data'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('upload_images/', views.upload_images, name='upload_images'),
    path("upload_genomic_information/", views.upload_genomic_information),
    #path('submit_phylogeny/', views.submit_phylogeny_task, name='submit_phylogeny'),
    path('query_status/<str:task_celery_id>/', views.query_task_status, name='query_task_status'),
    path('submit_sequences_with_db/', views.submit_sequences_with_db, name='submit_sequences_with_db'),
    path('query_split_tasks/',views.query_split_tasks,name='query_split_tasks'),
]
