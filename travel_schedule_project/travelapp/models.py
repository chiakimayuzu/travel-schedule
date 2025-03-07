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


PREFECTURES = [
    ('hokkaido', '北海道'),
    ('aomori', '青森県'),
    ('iwate', '岩手県'),
    ('miyagi', '宮城県'),
    ('akita', '秋田県'),
    ('yamagata', '山形県'),
    ('fukushima', '福島県'),
    ('ibaraki', '茨城県'),
    ('tochigi', '栃木県'),
    ('gunma', '群馬県'),
    ('saitama', '埼玉県'),
    ('chiba', '千葉県'),
    ('tokyo', '東京都'),
    ('kanagawa', '神奈川県'),
    ('niigata', '新潟県'),
    ('toyama', '富山県'),
    ('ishikawa', '石川県'),
    ('fukui', '福井県'),
    ('yamanashi', '山梨県'),
    ('nagano', '長野県'),
    ('gifu', '岐阜県'),
    ('shizuoka', '静岡県'),
    ('aichi', '愛知県'),
    ('mie', '三重県'),
    ('shiga', '滋賀県'),
    ('kyoto', '京都府'),
    ('osaka', '大阪府'),
    ('hyogo', '兵庫県'),
    ('nara', '奈良県'),
    ('wakayama', '和歌山県'),
    ('tottori', '鳥取県'),
    ('shimane', '島根県'),
    ('okayama', '岡山県'),
    ('hiroshima', '広島県'),
    ('yamaguchi', '山口県'),
    ('tokushima', '徳島県'),
    ('kagawa', '香川県'),
    ('ehime', '愛媛県'),
    ('kochi', '高知県'),
    ('fukuoka', '福岡県'),
    ('saga', '佐賀県'),
    ('nagasaki', '長崎県'),
    ('kumamoto', '熊本県'),
    ('oita', '大分県'),
    ('miyazaki', '宮崎県'),
    ('kagoshima', '鹿児島県'),
    ('okinawa', '沖縄県'),]

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
    (8,'不定休'),
]


PARKING_CHOICES = [
    (1, '有'),
    (2, '無'),
    (3, '不明'),
    (4, '注意(公式HP参照)'),]

class TouristSpot(models.Model):
    spot_name = models.CharField(max_length=50)
    prefecture = models.CharField(max_length=20, choices=PREFECTURES)
    address = models.CharField(max_length=100)
    tel = models.CharField(max_length=50)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    workingday = models.IntegerField(choices=WORKINGDAY_CHOICES,null=True, blank=True)
    parking = models.IntegerField(choices=PARKING_CHOICES)
    opening_at = models.TimeField(null=True, blank=True)
    closing_at = models.TimeField(null=True, blank=True)
    picture_url = models.CharField(max_length=100)
    description = models.TextField()
    offical_url = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 登録日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

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

    class Meta:
        unique_together = ('tourist_spot', 'keyword')

    def keywords_list(self):
        return ", ".join(self.touristspotkeyword_set.values_list("keyword__name", flat=True))

    def __str__(self):
        return f"{self.spot_name} ({self.keywords_list()})"

    def save(self, *args, **kwargs): #１つの観光地(touristspot)には10個のキーワードしか登録できない
        if TouristSpotKeyword.objects.filter(tourist_spot=self.tourist_spot).count() >= 10:
            raise ValidationError("1つの観光地に登録できるキーワードは10個までです")
        super().save(*args, **kwargs)   