from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)  # 重複不可にする
    email = models.EmailField(max_length=50, unique=True)  # 重複不可にする
    created_at = models.DateTimeField(auto_now_add=True)  # 登録日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    #AbstractUser内で競合するためnoneで設定しておく
    groups = None
    user_permissions = None

    USERNAME_FIELD = "email"  # メールアドレスでログイン
    REQUIRED_FIELDS = ["username"]  # `username` を必須フィールドに追加
        
    def __str__(self):
        return self.username

    class Meta:     
        db_table='Users'




#つづきはあとで
# class Tourist_spot(models.Model):
#     spot_name = models.CharField(max_length=50)
#     prefecture =
