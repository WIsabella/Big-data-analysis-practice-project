# mysite/celery.py

import os
from celery import Celery

# 设置 Django 环境的配置模块。
# 这里的参数格式是 '项目名.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings') 

# 实例化 Celery 应用。
# 'mysite' 应该替换为您的 Django 根项目名称
app = Celery('mysite') 

# 从 settings.py 中加载 Celery 配置（以 'CELERY_' 开头的设置）。
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册的 Django app（如 myapp）中的 tasks.py 文件。
app.autodiscover_tasks()