from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class OuterUser(AbstractUser):
    username = models.CharField(max_length=100, db_column='username', unique=True)
    password = models.CharField(max_length=200, db_column='password')
    email = models.EmailField(max_length=100, unique=True, db_column='email')
    type = models.CharField(max_length=10, db_column='type')
    organization = models.CharField(max_length=100, db_column='organization')

    objects = UserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        managed = False
        db_table = 'outer_user_outeruser'


class Order(models.Model):
    """
    记录订单状态的表
    """
    order_id = models.IntegerField(db_column='order_id', primary_key=True)
    customer = models.CharField(max_length=20, db_column='customer')
    institution = models.CharField(max_length=50, db_column='institution')
    contact1_type = models.CharField(max_length=20, db_column='contact1_type')
    contact1_value = models.CharField(max_length=50, db_column='contact1_value')
    contact2_type = models.CharField(max_length=20, db_column='contact2_type')
    contact2_value = models.CharField(max_length=50, db_column='contact2_value')
    purpose = models.CharField(max_length=100, db_column='purpose')
    create_data = models.DateTimeField(auto_now_add=True, db_column='create_data')
    bacteria_data = models.JSONField(db_column="bacteria_data", null=True)
    order_status = models.CharField(max_length=10, db_column="order_status", null=True)
    username = models.ForeignKey(to=OuterUser, on_delete=models.CASCADE, related_name="order", db_column="username", null=True)

    class Meta:
        managed = False
        db_table = 'orders'