# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# class Test1(models.Model):
#     deposit_number = models.CharField(db_column='Deposit_Number', primary_key=True, max_length=6, blank=False, null=False)
#     isolation_date = models.TextField(db_column='Isolation_Date', blank=True, null=True)  # Field name made lowercase.
#     isolator = models.TextField(db_column='Isolator', blank=True, null=True)  # Field name made lowercase.
#     original_strain_number = models.TextField(db_column='Original_Strain_Number', blank=True, null=True)  # Field name made lowercase.
#     closest_species = models.TextField(db_column='Closest_Species', blank=True, null=True)  # Field name made lowercase.
#     similarity_percentage = models.FloatField(db_column='Similarity_Percentage', blank=True, null=True)  # Field name made lowercase.
#     number_16s = models.TextField(db_column='16S', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
#     length = models.BigIntegerField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
#     accession = models.TextField(db_column='Accession', blank=True, null=True)  # Field name made lowercase.
#     taxonomic_unit = models.TextField(db_column='Taxonomic_Unit', blank=True, null=True)  # Field name made lowercase.
#     isolation_source = models.TextField(db_column='Isolation_Source', blank=True, null=True)  # Field name made lowercase.
#     sample_collection_time = models.TextField(db_column='Sample_Collection_Time', blank=True, null=True)  # Field name made lowercase.
#     gender = models.TextField(db_column='Gender', blank=True, null=True)  # Field name made lowercase.
#     age = models.FloatField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
#     health_status = models.TextField(db_column='Health_Status', blank=True, null=True)  # Field name made lowercase.
#     living_area = models.TextField(db_column='Living_Area', blank=True, null=True)  # Field name made lowercase.
#     bmi = models.FloatField(db_column='BMI', blank=True, null=True)  # Field name made lowercase.
#     isolation_medium = models.TextField(db_column='Isolation_Medium', blank=True, null=True)  # Field name made lowercase.
#     identification_medium = models.TextField(db_column='Identification_Medium', blank=True, null=True)  # Field name made lowercase.
#     culture_temperature = models.BigIntegerField(db_column='Culture_Temperature', blank=True, null=True)  # Field name made lowercase.
#     recommended_culture_time = models.BigIntegerField(db_column='Recommended_Culture_Time', blank=True, null=True)  # Field name made lowercase.
#     aerobicity = models.TextField(db_column='Aerobicity', blank=True, null=True)  # Field name made lowercase.
#     receipt_date = models.TextField(db_column='Receipt_Date', blank=True, null=True)  # Field name made lowercase.
#     slant_photo = models.CharField(db_column='Slant_Photo',blank=True,null=True,max_length=255,verbose_name='倾斜图片路径')
#     liquid_photo = models.CharField(db_column='Liquid_Photo',blank=True,null=True,max_length=255,verbose_name='液体图片路径')
#     slant_storage = models.BigIntegerField(db_column='Slant_Storage', blank=True, null=True)  # Field name made lowercase.
#     glycerol_preservation = models.BigIntegerField(db_column='Glycerol_Preservation', blank=True, null=True)  # Field name made lowercase.
#     lyophilization_preservation = models.BigIntegerField(db_column='Lyophilization_Preservation', blank=True, null=True)  # Field name made lowercase.
#     notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
#     metabolomics_data = models.TextField(db_column='Metabolomics_Data', blank=True, null=True)
#     genomic_information = models.TextField(db_column='Genomic_Information', blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = 'test1'
#     # 前端显示图片的绝对URL（核心辅助属性）
#     @property
#     def slant_photo_url(self):
#         if self.slant_photo:
#             from django.conf import settings
#             return os.path.join(settings.MEDIA_URL, self.slant_photo)
#         return ""

#     @property
#     def liquid_photo_url(self):
#         if self.liquid_photo:
#             from django.conf import settings
#             return os.path.join(settings.MEDIA_URL, self.liquid_photo)
#         return ""