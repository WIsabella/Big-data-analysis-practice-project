from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, role='student', **extra_fields):
        """创建并返回一个普通用户"""
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)  # 加密密码
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, role='teacher', **extra_fields):
        """创建并返回一个超级用户"""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')  # 默认为超级管理员
        return self.create_user(username, password, role, **extra_fields)

class QueraDataCustomuser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    students_pid = models.OneToOneField('Students', on_delete=models.CASCADE, to_field='pid',db_column='students_pid',default=1, related_name='account')

    USERNAME_FIELD = 'username'  # 使用 username 作为登录字段
    class Meta:
        managed = True
        db_table = 'quera_data_customuser'

class Students(models.Model):
    pid = models.AutoField(primary_key=True,db_column='pid', verbose_name="唯一标识")
    sduid = models.CharField(max_length = 20, db_column='student_id', verbose_name="学号")
    name = models.CharField(max_length=10, db_column='name', verbose_name='姓名', null=True)
    contact = models.CharField(max_length=50, db_column='contact', verbose_name='联系方式', null=True)

    class Meta:
        db_table = 'students_information'

