# travelapp/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from .models import UserReview

def update_touristspot_averages(tourist_spot):
    """ 観光地の平均評価、平均価格、平均滞在時間を更新 """
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot)

    if reviews.exists():
        tourist_spot.review_score_average = reviews.aggregate(Avg('review_score'))['review_score__avg']
        tourist_spot.price_average = reviews.aggregate(Avg(Cast('review_price', IntegerField())))['review_price__avg']
        tourist_spot.staytime_average = reviews.aggregate(Avg('stay_time_min'))['stay_time_min__avg']
    else:
        tourist_spot.review_score_average = None
        tourist_spot.price_average = None
        tourist_spot.staytime_average = None

    tourist_spot.save()

@receiver(post_save, sender=UserReview)
@receiver(post_delete, sender=UserReview)
def update_touristspot_on_review_change(sender, instance, **kwargs):
    """ レビューが追加・更新・削除された際に観光地情報を更新 """
    update_touristspot_averages(instance.tourist_spot)
