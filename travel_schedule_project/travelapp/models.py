from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from geopy.geocoders import GoogleV3
from django.conf import settings
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


PREFECTURE_CHOICES = [
    (1, '北海道'),
    (2, '青森県'),
    (3, '岩手県'),
    (4, '宮城県'),
    (5, '秋田県'),
    (6, '山形県'),
    (7, '福島県'),
    (8, '茨城県'),
    (9, '栃木県'),
    (10, '群馬県'),
    (11, '埼玉県'),
    (12, '千葉県'),
    (13, '東京都'),
    (14, '神奈川県'),
    (15, '新潟県'),
    (16, '富山県'),
    (17, '石川県'),
    (18, '福井県'),
    (19, '山梨県'),
    (20, '長野県'),
    (21, '岐阜県'),
    (22, '静岡県'),
    (23, '愛知県'),
    (24, '三重県'),
    (25, '滋賀県'),
    (26, '京都府'),
    (27, '大阪府'),
    (28, '兵庫県'),
    (29, '奈良県'),
    (30, '和歌山県'),
    (31, '鳥取県'),
    (32, '島根県'),
    (33, '岡山県'),
    (34, '広島県'),
    (35, '山口県'),
    (36, '徳島県'),
    (37, '香川県'),
    (38, '愛媛県'),
    (39, '高知県'),
    (40, '福岡県'),
    (41, '佐賀県'),
    (42, '長崎県'),
    (43, '熊本県'),
    (44, '大分県'),
    (45, '宮崎県'),
    (46, '鹿児島県'),
    (47, '沖縄県'),
]


CATEGORY_CHOICES = [
    (1,'神社/仏閣'),
    (2,'アクティビティ'),
    (3,'テーマパーク'),
    (4,'景勝'),
    (5,'その他'),
]

WORKINGDAY_CHOICES = [
    (1,'月曜'),
    (2,'火曜'),
    (3,'水曜'),
    (4,'木曜'),
    (5,'金曜'),
    (6,'土曜'),
    (7,'日曜'),
    (8,'年中無休'),
    (9,'不定休'),
]


PARKING_CHOICES = [
    (1, '有'),
    (2, '無'),
    (3, '不明'),
    (4, '注意(公式HP参照)'),]

class TouristSpot(models.Model):
    spot_name = models.CharField(max_length=50)
    prefecture = models.IntegerField(choices=PREFECTURE_CHOICES)
    address = models.CharField(max_length=100)
    tel = models.CharField(max_length=50)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    workingday = models.CharField(max_length=50, blank=True, null=True)
    parking = models.IntegerField(choices=PARKING_CHOICES)
    opening_at = models.TimeField(null=True, blank=True)
    closing_at = models.TimeField(null=True, blank=True)
    picture = models.ImageField(upload_to='tourist_spot_images/')  
    description = models.TextField()
    offical_url = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 登録日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日
    

    def save(self, *args, **kwargs):
        if self.address:  # 住所が入力されている場合
            geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
            location = geolocator.geocode(self.address)  # 住所から緯度・経度を取得
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        super().save(*args, **kwargs)  # 通常の保存処理を実行
    
    def __str__(self):
        return self.spot_name


class Keyword(models.Model):
    keyword = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword

class TouristSpotKeyword(models.Model):
    tourist_spot = models.ForeignKey(TouristSpot, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: #一つの観光地に同じkeywordが登録されないよう設定
        unique_together = ('tourist_spot', 'keyword')

    def keywords_list(self):
        return ", ".join(self.touristspotkeyword_set.values_list("keyword__name", flat=True))

    def __str__(self):
        return f"{self.spot_name} ({self.keywords_list()})"

    def save(self, *args, **kwargs): #１つの観光地(touristspot)には10個のキーワードしか登録できない
        if TouristSpotKeyword.objects.filter(tourist_spot=self.tourist_spot).count() >= 10:
            raise ValidationError("1つの観光地に登録できるキーワードは10個までです")
        super().save(*args, **kwargs)   