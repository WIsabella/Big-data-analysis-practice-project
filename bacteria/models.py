# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('QueraDataCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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

class QueraDataCustomuser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # 使用 username 作为登录字段
    REQUIRED_FIELDS = ['role']  # 创建用户时要求填写 role 字段
    class Meta:
        managed = False
        db_table = 'quera_data_customuser'




class Test1(models.Model):
    deposit_number = models.TextField(db_column='Deposit_Number', primary_key=True, blank=True)  # Field name made lowercase.
    isolation_date = models.TextField(db_column='Isolation_Date', blank=True, null=True)  # Field name made lowercase.
    isolator = models.TextField(db_column='Isolator', blank=True, null=True)  # Field name made lowercase.
    original_strain_number = models.TextField(db_column='Original_Strain_Number', blank=True, null=True)  # Field name made lowercase.
    closest_species = models.TextField(db_column='Closest_Species', blank=True, null=True)  # Field name made lowercase.
    similarity_percentage = models.FloatField(db_column='Similarity_Percentage', blank=True, null=True)  # Field name made lowercase.
    number_16s = models.TextField(db_column='16S', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    length = models.BigIntegerField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    accession = models.TextField(db_column='Accession', blank=True, null=True)  # Field name made lowercase.
    taxonomic_unit = models.TextField(db_column='Taxonomic_Unit', blank=True, null=True)  # Field name made lowercase.
    isolation_source = models.TextField(db_column='Isolation_Source', blank=True, null=True)  # Field name made lowercase.
    sample_collection_time = models.TextField(db_column='Sample_Collection_Time', blank=True, null=True)  # Field name made lowercase.
    gender = models.TextField(db_column='Gender', blank=True, null=True)  # Field name made lowercase.
    age = models.FloatField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    health_status = models.TextField(db_column='Health_Status', blank=True, null=True)  # Field name made lowercase.
    living_area = models.TextField(db_column='Living_Area', blank=True, null=True)  # Field name made lowercase.
    bmi = models.FloatField(db_column='BMI', blank=True, null=True)  # Field name made lowercase.
    isolation_medium = models.TextField(db_column='Isolation_Medium', blank=True, null=True)  # Field name made lowercase.
    identification_medium = models.TextField(db_column='Identification_Medium', blank=True, null=True)  # Field name made lowercase.
    culture_temperature = models.BigIntegerField(db_column='Culture_Temperature', blank=True, null=True)  # Field name made lowercase.
    recommended_culture_time = models.BigIntegerField(db_column='Recommended_Culture_Time', blank=True, null=True)  # Field name made lowercase.
    aerobicity = models.TextField(db_column='Aerobicity', blank=True, null=True)  # Field name made lowercase.
    receipt_date = models.TextField(db_column='Receipt_Date', blank=True, null=True)  # Field name made lowercase.
    slant_photo = models.TextField(db_column='Slant_Photo', blank=True, null=True)  # Field name made lowercase.
    liquid_photo = models.TextField(db_column='Liquid_Photo', blank=True, null=True)  # Field name made lowercase.
    slant_storage = models.BigIntegerField(db_column='Slant_Storage', blank=True, null=True)  # Field name made lowercase.
    glycerol_preservation = models.BigIntegerField(db_column='Glycerol_Preservation', blank=True, null=True)  # Field name made lowercase.
    lyophilization_preservation = models.BigIntegerField(db_column='Lyophilization_Preservation', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'test1'
