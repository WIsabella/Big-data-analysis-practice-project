'''该文件用于我手动的给数据库中的用户表添加用户和处理用户的权限授予问题'''
import os
import django
# 1. 告诉 Django 你的 settings 文件在哪
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
# 2. 初始化 Django 环境
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from bacteria.models import QueraDataCustomuser, Test1

if __name__ == '__main__':
    user = QueraDataCustomuser.objects.create_user(username='test3', password='123456', role='student')
    content_type = ContentType.objects.get_for_model(Test1)
    user.user_permissions.add(Permission.objects.get(codename='view_test1', content_type=content_type))