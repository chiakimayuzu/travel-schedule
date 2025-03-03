from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # auto_now_add=Trueで登録日がnowでDB保存
    update_at = models.DateTimeField(auto_now_add=True)  # auto_now_add=Trueでaudate日がnowでDB保存

    def __str__(self):
        return self.title

    class Meta:     
        db_table='User'