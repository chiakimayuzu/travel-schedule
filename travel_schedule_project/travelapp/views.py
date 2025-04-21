import os
import random
from typing import Counter
from venv import logger
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView,UpdateView
from django.contrib.auth.models import User
from .forms import ChangeEmailForm, PasswordChangeForm, RegistAccountForm, TouristPlanSpotFormSet, TouristSpotSearchForm, UserLoginForm, UserReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from .forms import TouristSpotForm
from .models import CATEGORY_CHOICES, PREFECTURE_CHOICES, REVIEW_PRICE_CHOICES, Keyword, TouristSpot, TouristSpotKeyword, UserReview, WantedSpot
from django.shortcuts import render, redirect
from .forms import TouristSpotForm, UserReviewForm
from .models import Keyword, TouristSpotKeyword
from geopy.geocoders import GoogleV3
from django.conf import settings
from .models import TouristSpot, TouristSpotKeyword, WORKINGDAY_CHOICES, UserReview
from django.views import View
from django.db.models import Avg
from django.db.models import Q
from django.views.generic.list import ListView
from django.shortcuts import render
from django.db.models import Q
from .forms import TouristSpotSearchForm
from .models import TouristSpot
from django.db.models import Q
from .forms import TouristSpotSearchForm
from .models import TouristSpot
from collections import Counter
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from .models import TouristSpot, TouristSpotKeyword, UserReview, WantedSpot
from collections import Counter
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from .models import TouristSpot, TouristSpotKeyword, UserReview, WantedSpot
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TouristSpot, TouristPlan, TouristPlan_Spot, WantedSpot
from .forms import TouristPlanForm
from datetime import datetime, timedelta
from urllib.parse import unquote
from urllib.parse import urlencode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib.auth import get_user_model
from collections import defaultdict
# Create your views here.


class RegistAccountView(View):
    def get(self, request):
        form = RegistAccountForm()
        return render(request, 'account/regist_account.html', {'form': form})

    def post(self, request):
        form = RegistAccountForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ユーザーをログインさせる
            return redirect('travelapp:home')  # ホーム画面にリダイレクト(.html不要)

        else:   
            # フォームが無効な場合、エラーメッセージを表示
            for field in form:
                for error in field.errors:  # 各フィールドのエラーを取り出して表示
                    messages.error(request, error)  # エラーをメッセージとして表示
            return render(request, 'account/regist_account.html', {'form': form})  # フォームを再表示


class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, "account/user_login.html", {
            "form": form,
            # form_errors は渡さない
        })

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect("travelapp:home")
        return render(request, "account/user_login.html", {
            "form": form,
            "form_errors": form.non_field_errors()
        })

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)  # GET でもログアウト処理を実行
        return redirect('travelapp:home')  # 直接ホームにリダイレクト

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('travelapp:home')




@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(user=request.user, data=request.POST)
        if form.is_valid():
            # メールアドレスの更新処理
            request.user.email = form.cleaned_data['new_email']
            request.user.save()
            # 成功メッセージを追加してリダイレクト
            messages.success(request, 'メールアドレス変更できました', extra_tags='change_email')
            return redirect('travelapp:change_email')  # プロフィールページなどの適切なリダイレクト先に変更してください
    else:
        form = ChangeEmailForm(user=request.user)
    
    return render(request, 'account/change_email.html', {'form': form})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # パスワード変更後もログイン状態を保持
            messages.success(request, 'パスワード変更できました', extra_tags='change_password') # 成功メッセージが同じページに表示されるようにします
            return redirect('travelapp:change_password')  
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})


class PortfolioView(View):
    def get(self, request):
        return render(request, "portfolio.html")



def home(request):
    form = TouristSpotSearchForm(request.GET or None)
    
    if request.GET and form.is_valid():
        return redirect('travelapp:search_touristspot')
    
    # ✅ 登録されているTouristSpotをランダムに1つ取得
    tourist_spot = None
    latest_review = None

    spots = TouristSpot.objects.all()
    if spots.exists():
        tourist_spot = random.choice(spots)
        # ✅ ランダムで取得したTouristSpotに関連する最新のレビューを取得
        latest_review = tourist_spot.userreview_set.order_by('-created_at').first()

        # カテゴリ選択肢を定義
    category_choices = [(value, name) for value, name in CATEGORY_CHOICES]


    context = {
        'form': form,
        'tourist_spot': tourist_spot,
        'latest_review': latest_review,
        'category_choices': category_choices,
    }
    return render(request, 'home.html', context)
    


class TouristSpotSearchView(ListView):
    model = TouristSpot
    template_name = 'search_touristspot.html'
    context_object_name = 'tourist_spots'

    def get_queryset(self):
        queryset = TouristSpot.objects.all()
        keyword = self.request.GET.get('query')  # 'query' パラメータを取得
        category = self.request.GET.get('category')

        if keyword:
            # PREFECTURE_CHOICESを辞書にして、入力されたキーワードを対応する値に変換
            prefecture_dict = dict(PREFECTURE_CHOICES)

            # 県名（例：京都府）を入力された場合、その番号（例：26）を取得
            prefecture_value = None
            for value, name in prefecture_dict.items():
                if name in keyword:
                    prefecture_value = value
                    break

            # 県名が見つかった場合、prefectureでフィルタリング
            if prefecture_value:
                queryset = queryset.filter(prefecture=prefecture_value)
            else:
                # 県名に一致しない場合は、他のフィールドで検索を続ける
                queryset = queryset.filter(
                    Q(spot_name__icontains=keyword) |
                    Q(address__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(touristspotkeyword__keyword__keyword__icontains=keyword)  # TouristSpotKeywordを使ってキーワードを検索
                )

        if category:
            # カテゴリによるフィルタリング
            queryset = queryset.filter(category=category)

        # 並び順の処理
        sort_by = self.request.GET.get('sort', '-created_at')  # デフォルトは評価がいい順
        if sort_by == '-created_at':
            queryset = queryset.order_by('-created_at')  # 評価がいい順
        elif sort_by == 'created_at':
            queryset = queryset.order_by('created_at')  # 登録が古い順

        return queryset.distinct()


@login_required
def regist_touristspot(request):
    if request.method == "POST":
        form = TouristSpotForm(request.POST, request.FILES)
        if form.is_valid():
            tourist_spot = form.save(commit=False)  # ★一旦保存を遅らせる

            # 住所から緯度・経度を取得の処理
            if tourist_spot.address:  # 住所が入力されている場合
                geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
                location = geolocator.geocode(tourist_spot.address)  # 住所から緯度・経度を取得
                if location:
                    tourist_spot.latitude = location.latitude
                    tourist_spot.longitude = location.longitude
                else:
                    # 住所が無効な場合にエラーメッセージを追加するなどの処理を行う
                    form.add_error('address', '住所に対応する位置情報が見つかりませんでした。')
            
            # workingday をカンマ区切りの文字列に変換
            workingdays = form.cleaned_data.get("workingday")
            if workingdays:
                tourist_spot.workingday = ",".join(map(str, workingdays))

            # キーワードの保存処理
            keywords_text = form.cleaned_data.get("keywords")

            if isinstance(keywords_text, list):  
                keywords_list = [kw.strip() for kw in keywords_text if kw.strip()]
            elif isinstance(keywords_text, str):  
                keywords_list = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            else:  
                keywords_list = []

            # キーワードを保存
            for keyword_text in keywords_list:
                keyword, created = Keyword.objects.get_or_create(keyword=keyword_text)

                 # 新規作成の場合でも保存する
                keyword.save()  # ここで毎回保存

                # ★ tourist_spot が未保存なら先に保存
                if not tourist_spot.pk:
                    tourist_spot.save()

                 # TouristSpotKeyword に関連付け
                TouristSpotKeyword.objects.create(tourist_spot=tourist_spot, keyword=keyword)  # ここで関連付け

            tourist_spot.save()  # 観光地情報を保存する
            messages.success(request, '観光地登録できました', extra_tags='regist_touristspot') # 成功メッセージが同じページに表示されるようにします
            return redirect(reverse('travelapp:regist_touristspot'))  # ビュー名でリダイレクト

    else:
        form = TouristSpotForm()

    return render(request, 'regist_touristspot.html', {'form': form})

def check_username(request):  # 入力されたusernameが既に存在するかを確認
    username = request.GET.get('username')  # フォームの入力値を取得

    Users = get_user_model()

    username_exists = False
    if username:
        username_exists = Users.objects.filter(username=username).exists()  # usernameが既に存在するか確認

    return JsonResponse({'username_exists': username_exists})  # exists が True ならusernameが存在、エラー表示

def check_email(request):  # 入力されたusernameが既に存在するかを確認
    email = request.GET.get('email')  # フォームの入力値を取得

    Users = get_user_model()

    email_exists = False
    if email:
        email_exists = Users.objects.filter(email=email).exists()  # usernameが既に存在するか確認

    return JsonResponse({'email_exists': email_exists})  # exists が True ならemailが存在、エラー表示

def check_dupe_tourist_spot(request):
    spot_name = request.GET.get('spot_name', '').strip()
    address = request.GET.get('address', '').strip()

    # 条件に基づいてエラーを設定
    spot_name_exists = False
    address_exists = False
    if spot_name:
        spot_name_exists = TouristSpot.objects.filter(spot_name=spot_name).exists()
    if address:
        address_exists = TouristSpot.objects.filter(address=address).exists()

    return JsonResponse({
        'spot_name_exists': spot_name_exists,
        'address_exists': address_exists
    })



def detail_touristspot(request, pk):
    # 観光地情報をID（pk）で取得
    tourist_spot = get_object_or_404(TouristSpot, pk=pk)
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    # workingday を曜日名に変換
    day_mapping = dict(WORKINGDAY_CHOICES)
    working_days = []
    if tourist_spot.workingday:
        # workingdayのデータをカンマ区切りで分割して、曜日名に変換
        working_days = [day_mapping.get(int(day), day) for day in tourist_spot.workingday.split(",") if day.strip().isdigit()]

    # TouristSpotKeyword から keyword を取得
    keywords = TouristSpotKeyword.objects.filter(tourist_spot=tourist_spot).values_list('keyword__keyword', flat=True)

    # その観光地に関連するクチコミを作成日時順に並べ替えて最新の3件を取得
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')[:3]

    # 各平均値を計算
    review_score_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('review_score'))['review_score__avg']
    # 小数点第一位まで丸める
    review_score_avg = round(review_score_avg, 1) if review_score_avg is not None else 0
    price_avg = UserReview.objects.filter(tourist_spot=tourist_spot).values('review_price')
    stay_time_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('stay_time_min'))['stay_time_min__avg']

    # もし平均値がNoneの場合は、0を代入
    review_score_avg = review_score_avg if review_score_avg is not None else 0
    stay_time_avg = stay_time_avg if stay_time_avg is not None else 0

    # 価格帯の最頻値を取得
    price_counter = Counter([price['review_price'] for price in price_avg])
    most_common_price = price_counter.most_common(1)
    most_common_price = most_common_price[0][0] if most_common_price else None

    # REVIEW_PRICE_CHOICES の dict を作成
    price_choices_dict = dict(REVIEW_PRICE_CHOICES)

    # 最頻値の価格帯を取得し、対応する価格帯の文字列に変換
    most_common_price_str = price_choices_dict.get(most_common_price, "情報なし")

    # 滞在時間の表示形式（時間と分
    if stay_time_avg and stay_time_avg > 0:  # stay_time_avg が None または 0 でない場合
        stay_time_hours = int(stay_time_avg) // 60
        stay_time_minutes = int(stay_time_avg) % 60
        stay_time_display = f"{stay_time_hours}時間 {stay_time_minutes}分"
    else:
        stay_time_display = "情報なし"  # 情報がない場合は「情報なし」と表示
        stay_time_hours = None  # 変数を None に設定してエラーを防止
        stay_time_minutes = None 

    # クチコミ件数を取得
    review_count = UserReview.objects.filter(tourist_spot=tourist_spot).count()

    # ★（塗りつぶし星・半分の星・空の星）の表示制御
    # 整数部分の塗りつぶし星
    filled_stars = int(review_score_avg)  # 整数部分の塗りつぶし
    # 小数部分（0.25以上なら半分塗りつぶし）
    half_star = (review_score_avg - filled_stars) >= 0.5  # 0.25以上で半分星
    # 空の星（5個になるように調整）
    empty_stars = 5 - filled_stars - (1 if half_star else 0)

    # ログインしていない場合は行きたいリストに追加されていないと見なす
    is_wanted = False
    if request.user.is_authenticated:
        # ログインしている場合のみ行きたいリストを確認
        is_wanted = WantedSpot.objects.filter(user=request.user, tourist_spot=tourist_spot).exists()

    # テンプレートに渡すコンテキスト
    context = {
        'tourist_spot': tourist_spot,   # 観光地情報
        'working_days': working_days,   # 営業曜日
        'keywords': keywords,           # キーワード
        'reviews': reviews,             # クチコミ一覧
        'is_wanted': is_wanted,         # 行きたいリストに含まれているか
        'review_score_avg': review_score_avg, # 評価スコア平均
        'price_avg': price_avg,         # 価格帯
        'stay_time_avg': stay_time_avg, # 滞在時間平均（分）
        'filled_stars': range(filled_stars),   # 塗りつぶし星の数（リスト）
        'half_star': half_star,         # 半分塗りつぶしの星
        'empty_stars': range(empty_stars),     # 空の星の数（リスト）
        'stay_time_hours': stay_time_hours, # 滞在時間（時間）
        'stay_time_minutes': stay_time_minutes, # 滞在時間（分）
        'most_common_price': most_common_price_str, # 価格帯（最頻値）
        'review_count': review_count,   # クチコミ件数
        'google_maps_api_key': google_maps_api_key, # APIキーを渡す
        'stay_time_display':stay_time_display
    }

    return render(request, 'detail_touristspot.html', context)



def edit_touristspot(request, pk):
    tourist_spot = get_object_or_404(TouristSpot, pk=pk)
    
    # 現在登録されているキーワードを取得
    current_keywords = tourist_spot.touristspotkeyword_set.all()

    # 現在登録されているワーキングデイをリスト化
    current_workingdays = tourist_spot.workingday.split(",") if tourist_spot.workingday else []
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')[:3]
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    # workingday を曜日名に変換
    day_mapping = dict(WORKINGDAY_CHOICES)
    working_days = []
    if tourist_spot.workingday:
        # workingdayのデータをカンマ区切りで分割して、曜日名に変換
        working_days = [day_mapping.get(int(day), day) for day in tourist_spot.workingday.split(",") if day.strip().isdigit()]

    # TouristSpotKeyword から keyword を取得
    keywords = TouristSpotKeyword.objects.filter(tourist_spot=tourist_spot).values_list('keyword__keyword', flat=True)

    # その観光地に関連するクチコミを作成日時順に並べ替えて最新の3件を取得
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')[:3]

    # 各平均値を計算
    review_score_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('review_score'))['review_score__avg']
    # 小数点第一位まで丸める
    review_score_avg = round(review_score_avg, 1) if review_score_avg is not None else 0    
    price_avg = UserReview.objects.filter(tourist_spot=tourist_spot).values('review_price')
    stay_time_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('stay_time_min'))['stay_time_min__avg']

    # もし平均値がNoneの場合は、0を代入
    review_score_avg = review_score_avg if review_score_avg is not None else 0
    stay_time_avg = stay_time_avg if stay_time_avg is not None else 0

    # 価格帯の最頻値を取得
    price_counter = Counter([price['review_price'] for price in price_avg])
    most_common_price = price_counter.most_common(1)
    most_common_price = most_common_price[0][0] if most_common_price else None

    # REVIEW_PRICE_CHOICES の dict を作成
    price_choices_dict = dict(REVIEW_PRICE_CHOICES)

    # 最頻値の価格帯を取得し、対応する価格帯の文字列に変換
    most_common_price_str = price_choices_dict.get(most_common_price, "情報なし")

    # 滞在時間の表示形式（時間と分）
    if stay_time_avg and stay_time_avg > 0:  # stay_time_avg が None または 0 でない場合
        stay_time_hours = int(stay_time_avg) // 60
        stay_time_minutes = int(stay_time_avg) % 60
        stay_time_display = f"{stay_time_hours}時間 {stay_time_minutes}分"
    else:
        stay_time_display = "情報なし"  # 情報がない場合は「情報なし」と表示
        stay_time_hours = None  # 変数を None に設定してエラーを防止
        stay_time_minutes = None 

    # クチコミ件数を取得
    review_count = UserReview.objects.filter(tourist_spot=tourist_spot).count()

    # ★（塗りつぶし星・半分の星・空の星）の表示制御
    # 整数部分の塗りつぶし星
    filled_stars = int(review_score_avg)  # 整数部分の塗りつぶし
    # 小数部分（0.25以上なら半分塗りつぶし）
    half_star = (review_score_avg - filled_stars) >= 0.5  # 0.25以上で半分星
    # 空の星（5個になるように調整）
    empty_stars = 5 - filled_stars - (1 if half_star else 0)

    # ログインしていない場合は行きたいリストに追加されていないと見なす
    is_wanted = False
    if request.user.is_authenticated:
        # ログインしている場合のみ行きたいリストを確認
        is_wanted = WantedSpot.objects.filter(user=request.user, tourist_spot=tourist_spot).exists()

    # ログインしていない場合、メッセージを渡す
    if not request.user.is_authenticated:
    # 同じページにメッセージを表示
        return render(request, 'detail_touristspot.html', {
            'tourist_spot': tourist_spot,
            'working_days': working_days,   # 営業曜日
            'keywords': keywords,           # キーワード
            'reviews': reviews,             # クチコミ一覧
            'is_wanted': is_wanted,         # 行きたいリストに含まれているか
            'review_score_avg': review_score_avg, # 評価スコア平均
            'price_avg': price_avg,         # 価格帯
            'stay_time_avg': stay_time_avg, # 滞在時間平均（分）
            'filled_stars': range(filled_stars),   # 塗りつぶし星の数（リスト）
            'half_star': half_star,         # 半分塗りつぶしの星
            'empty_stars': range(empty_stars),     # 空の星の数（リスト）
            'stay_time_hours': stay_time_hours, # 滞在時間（時間）
            'stay_time_minutes': stay_time_minutes, # 滞在時間（分）
            'most_common_price': most_common_price_str, # 価格帯（最頻値）
            'review_count': review_count,   # クチコミ件数
            'google_maps_api_key': google_maps_api_key,  # APIキーを渡す
            'stay_time_display':stay_time_display,

            'error_message': "この機能を利用するにはログインしてください。",
    })

    if request.method == 'POST':
        form = TouristSpotForm(request.POST, request.FILES, instance=tourist_spot)

        if form.is_valid():
            # 新しいキーワードの処理
            new_keywords = request.POST.getlist('keywords')
            new_keywords = [kw.strip() for kw in new_keywords if kw.strip()]
            
            # 現在のキーワードを削除
            tourist_spot.touristspotkeyword_set.all().delete()

            # 新しいキーワードを追加
            for keyword in new_keywords:
                keyword_obj, created = Keyword.objects.get_or_create(keyword=keyword)
                TouristSpotKeyword.objects.create(tourist_spot=tourist_spot, keyword=keyword_obj)

            # ワーキングデイの処理
            workingdays = request.POST.getlist('workingday')
            tourist_spot.workingday = ",".join(workingdays)

            # フォームを保存
            tourist_spot.save()
            messages.success(request, '観光地編集できました', extra_tags='detail_touristspot')
            return redirect('travelapp:detail_touristspot', pk=tourist_spot.pk)

    else:
        form = TouristSpotForm(instance=tourist_spot)

    return render(request, 'edit_touristspot.html', {
        'form': form,
        'tourist_spot': tourist_spot,
        'current_keywords': current_keywords,
        'current_workingdays': current_workingdays,
    })




def create_review(request, pk):  # 🔹 引数名を pk に変更
    tourist_spot = get_object_or_404(TouristSpot, id=pk)
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    # workingday を曜日名に変換
    day_mapping = dict(WORKINGDAY_CHOICES)
    working_days = []
    if tourist_spot.workingday:
        # workingdayのデータをカンマ区切りで分割して、曜日名に変換
        working_days = [day_mapping.get(int(day), day) for day in tourist_spot.workingday.split(",") if day.strip().isdigit()]

    # TouristSpotKeyword から keyword を取得
    keywords = TouristSpotKeyword.objects.filter(tourist_spot=tourist_spot).values_list('keyword__keyword', flat=True)

    # その観光地に関連するクチコミを作成日時順に並べ替えて最新の3件を取得
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')[:3]

    # 各平均値を計算
    review_score_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('review_score'))['review_score__avg']
    # 小数点第一位まで丸める
    review_score_avg = round(review_score_avg, 1) if review_score_avg is not None else 0
    price_avg = UserReview.objects.filter(tourist_spot=tourist_spot).values('review_price')
    stay_time_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('stay_time_min'))['stay_time_min__avg']

    # もし平均値がNoneの場合は、0を代入
    review_score_avg = review_score_avg if review_score_avg is not None else 0
    stay_time_avg = stay_time_avg if stay_time_avg is not None else 0

    # 価格帯の最頻値を取得
    price_counter = Counter([price['review_price'] for price in price_avg])
    most_common_price = price_counter.most_common(1)
    most_common_price = most_common_price[0][0] if most_common_price else None

    # REVIEW_PRICE_CHOICES の dict を作成
    price_choices_dict = dict(REVIEW_PRICE_CHOICES)

    # 最頻値の価格帯を取得し、対応する価格帯の文字列に変換
    most_common_price_str = price_choices_dict.get(most_common_price, "情報なし")

    # 滞在時間の表示形式（時間と分）
    if stay_time_avg and stay_time_avg > 0:  # stay_time_avg が None または 0 でない場合
        stay_time_hours = int(stay_time_avg) // 60
        stay_time_minutes = int(stay_time_avg) % 60
        stay_time_display = f"{stay_time_hours}時間 {stay_time_minutes}分"
    else:
        stay_time_display = "情報なし"  # 情報がない場合は「情報なし」と表示
        stay_time_hours = None  # 変数を None に設定してエラーを防止
        stay_time_minutes = None 

    # クチコミ件数を取得
    review_count = UserReview.objects.filter(tourist_spot=tourist_spot).count()

    # ★（塗りつぶし星・半分の星・空の星）の表示制御
    # 整数部分の塗りつぶし星
    filled_stars = int(review_score_avg)  # 整数部分の塗りつぶし
    # 小数部分（0.25以上なら半分塗りつぶし）
    half_star = (review_score_avg - filled_stars) >= 0.5  # 0.5以上で半分星
    # 空の星（5個になるように調整）
    empty_stars = 5 - filled_stars - (1 if half_star else 0)

    # ログインしていない場合は行きたいリストに追加されていないと見なす
    is_wanted = False
    if request.user.is_authenticated:
        # ログインしている場合のみ行きたいリストを確認
        is_wanted = WantedSpot.objects.filter(user=request.user, tourist_spot=tourist_spot).exists()

    # ログインしていない場合、メッセージを渡す
    if not request.user.is_authenticated:
        # 同じページにメッセージを表示
        return render(request, 'detail_touristspot.html', {
            'tourist_spot': tourist_spot,
            'working_days': working_days,   # 営業曜日
            'keywords': keywords,           # キーワード
            'reviews': reviews,             # クチコミ一覧
            'is_wanted': is_wanted,         # 行きたいリストに含まれているか
            'review_score_avg': review_score_avg, # 評価スコア平均
            'price_avg': price_avg,         # 価格帯
            'stay_time_avg': stay_time_avg, # 滞在時間平均（分）
            'filled_stars': range(filled_stars),   # 塗りつぶし星の数（リスト）
            'half_star': half_star,         # 半分塗りつぶしの星
            'empty_stars': range(empty_stars),     # 空の星の数（リスト）
            'stay_time_hours': stay_time_hours, # 滞在時間（時間）
            'stay_time_minutes': stay_time_minutes, # 滞在時間（分）
            'most_common_price': most_common_price_str, # 価格帯（最頻値）
            'review_count': review_count,   # クチコミ件数
            'google_maps_api_key': google_maps_api_key,  # APIキーを渡す
            'error_message': "この機能を利用するにはログインしてください。",
            'stay_time_display':stay_time_display
        })


    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)  # インスタンスをまだデータベースに保存しない

            # stay_time_min を手動で設定
            stay_time_hours = form.cleaned_data['stay_time_hours']
            stay_time_minutes = form.cleaned_data['stay_time_minutes']
            stay_time_min = int(stay_time_hours) * 60 + int(stay_time_minutes)
            review.stay_time_min = stay_time_min  # stay_time_min を設定

            review.tourist_spot = tourist_spot  # 観光地を設定
            review.user = request.user  # 現在のログインユーザーを設定
            review.save()  # 保存
       
            messages.success(request, 'レビュー作成できました', extra_tags='create_review')
            return redirect('travelapp:detail_touristspot', pk=tourist_spot.pk)
    else:
        form = UserReviewForm()
    
    context = {
        'form':form,
        'tourist_spot':tourist_spot
    }

    return render(request, 'reviews/create_review.html', context)

@login_required
def my_review_list(request):       
    reviews = UserReview.objects.filter(user=request.user).order_by('-created_at')  
                            #ログインユーザーのクチコミを取得・↑新い順に並べる/編集も可能なのでupdate_atにて

    # レビュー削除処理
    if request.method == "POST" and 'delete' in request.POST:
        review_id = request.POST['delete']
        review = get_object_or_404(UserReview, id=review_id, user=request.user)
        review.delete()
        return redirect(reverse('travelapp:my_review_list'))  # 削除後にリストページにリダイレクト

    for review in reviews:
        review.stay_time_hours = review.stay_time_min // 60
        review.stay_time_minutes = review.stay_time_min % 60

    context = {
        'reviews': reviews
    }   
    return render(request, 'reviews/my_review_list.html', context)


@login_required
def my_review_detail(request, review_id):
    # ユーザーが投稿したレビューを取得
    review = get_object_or_404(UserReview, id=review_id, user=request.user)

    # 滞在時間の変換（時間と分に分割）
    review.stay_time_hours = review.stay_time_min // 60
    review.stay_time_minutes = review.stay_time_min % 60

    # 塗りつぶしと空の星のリストを作成
    filled_stars = range(review.review_score)  # 塗りつぶしの星
    empty_stars = range(5 - review.review_score)  # 空の星


    if request.method == 'POST' and 'delete' in request.POST:
        review.delete()
        return redirect(reverse('travelapp:my_review_list'))

    context = {
        'review': review,
        'filled_stars': filled_stars,
        'empty_stars': empty_stars,
    }

    return render(request, 'reviews/my_review_detail.html', context)


# 既存レビュー編集ビュー
@login_required
def edit_my_review(request, pk):  # 引数を review_id から pk に変更
    review = get_object_or_404(UserReview, pk=pk, user=request.user)  # id を pk に変更
    
    # 既存のフォームにレビュー内容を設定
    if request.method == 'POST':
        form = UserReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'レビュー編集できました', extra_tags='review_list')
            return redirect('travelapp:my_review_detail', review_id=review.id)  # リダイレクト先も review_id から pk に変更
    else:
        form = UserReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review
    }
    return render(request, 'reviews/edit_my_review.html', context)    


def review_list(request, pk):
    # 観光地情報をID（pk）で取得
    tourist_spot = get_object_or_404(TouristSpot, pk=pk)

    # その観光地に関連するクチコミを作成日時順に並べ替えて全件取得
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')

    # テンプレートに渡すコンテキスト
    context = {
        'tourist_spot': tourist_spot,
        'reviews': reviews,
    }

    return render(request, 'reviews/review_list.html', context)



def wanted_spot(request, tourist_spot_id):
    tourist_spot = TouristSpot.objects.get(id=tourist_spot_id)
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    # workingday を曜日名に変換
    day_mapping = dict(WORKINGDAY_CHOICES)
    working_days = []
    if tourist_spot.workingday:
        # workingdayのデータをカンマ区切りで分割して、曜日名に変換
        working_days = [day_mapping.get(int(day), day) for day in tourist_spot.workingday.split(",") if day.strip().isdigit()]
        
    # TouristSpotKeyword から keyword を取得
    keywords = TouristSpotKeyword.objects.filter(tourist_spot=tourist_spot).values_list('keyword__keyword', flat=True)

    # その観光地に関連するクチコミを作成日時順に並べ替えて最新の3件を取得
    reviews = UserReview.objects.filter(tourist_spot=tourist_spot).order_by('-created_at')[:3]

    # 各平均値を計算
    review_score_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('review_score'))['review_score__avg']
    price_avg = UserReview.objects.filter(tourist_spot=tourist_spot).values('review_price')
    stay_time_avg = UserReview.objects.filter(tourist_spot=tourist_spot).aggregate(Avg('stay_time_min'))['stay_time_min__avg']

    # もし平均値がNoneの場合は、0を代入
    review_score_avg = review_score_avg if review_score_avg is not None else 0
    stay_time_avg = stay_time_avg if stay_time_avg is not None else 0

    # 価格帯の最頻値を取得
    price_counter = Counter([price['review_price'] for price in price_avg])
    most_common_price = price_counter.most_common(1)
    most_common_price = most_common_price[0][0] if most_common_price else None

    # REVIEW_PRICE_CHOICES の dict を作成
    price_choices_dict = dict(REVIEW_PRICE_CHOICES)

    # 最頻値の価格帯を取得し、対応する価格帯の文字列に変換
    most_common_price_str = price_choices_dict.get(most_common_price, "情報なし")

    # 滞在時間の表示形式（時間と分）
    stay_time_hours = int(stay_time_avg) // 60
    stay_time_minutes = int(stay_time_avg) % 60

    # 滞在時間の表示形式（時間と分）
    if stay_time_avg and stay_time_avg > 0:  # stay_time_avg が None または 0 でない場合
        stay_time_hours = int(stay_time_avg) // 60
        stay_time_minutes = int(stay_time_avg) % 60
        stay_time_display = f"{stay_time_hours}時間 {stay_time_minutes}分"
    else:
        stay_time_display = "情報なし"  # 情報がない場合は「情報なし」と表示
        stay_time_hours = None  # 変数を None に設定してエラーを防止
        stay_time_minutes = None 
    

    # クチコミ件数を取得
    review_count = UserReview.objects.filter(tourist_spot=tourist_spot).count()

    # ★（塗りつぶし星・半分の星・空の星）の表示制御
    # 整数部分の塗りつぶし星
    filled_stars = int(review_score_avg)  # 整数部分の塗りつぶし
    # 小数部分（0.25以上なら半分塗りつぶし）
    half_star = (review_score_avg - filled_stars) >= 0.25  # 0.25以上で半分星
    # 空の星（5個になるように調整）
    empty_stars = 5 - filled_stars - (1 if half_star else 0)





    # ログインしていない場合、メッセージを渡す
    if not request.user.is_authenticated:
    # 同じページにメッセージを表示
        return render(request, 'detail_touristspot.html', {
            'tourist_spot': tourist_spot,
            'google_maps_api_key': google_maps_api_key,  # APIキーを渡す
            'tourist_spot': tourist_spot,   # 観光地情報
            'working_days': working_days,   # 営業曜日
            'keywords': keywords,           # キーワード
            'reviews': reviews,             # クチコミ一覧
            'review_score_avg': review_score_avg, # 評価スコア平均
            'price_avg': price_avg,         # 価格帯
            'stay_time_avg': stay_time_avg, # 滞在時間平均（分）
            'filled_stars': [i for i in range(filled_stars)],   # 塗りつぶし星の数（リスト）
            'half_star': half_star,         # 半分塗りつぶしの星
            'empty_stars': [i for i in range(empty_stars)],     # 空の星の数（リスト）
            'stay_time_hours': stay_time_hours, # 滞在時間（時間）
            'stay_time_minutes': stay_time_minutes, # 滞在時間（分）
            'most_common_price': most_common_price_str, # 価格帯（最頻値）
            'review_count': review_count,   # クチコミ件数
            'stay_time_display':stay_time_display,
            'error_message': "この機能を利用するにはログインしてください。",
        })

    if WantedSpot.objects.filter(user=request.user, tourist_spot=tourist_spot).exists():
        return HttpResponse("すでに行きたいリストに追加されています。")

    # 行きたいリストに追加
    WantedSpot.objects.create(user=request.user, tourist_spot=tourist_spot)

    # 詳細ページにリダイレクト
    return redirect('travelapp:detail_touristspot', pk=tourist_spot.id)



@login_required
def wanted_spot_list(request):
    # ログインしているユーザーの行きたいリストを取得
    wanted_spots = WantedSpot.objects.filter(user=request.user)

    if request.method == 'POST' and 'delete' in request.POST:
        # 削除処理
        wanted_spot_id = request.POST.get('delete')
        wanted_spot = WantedSpot.objects.get(id=wanted_spot_id)
        wanted_spot.delete()

        return redirect('travelapp:wanted_spot_list')

    return render(request, 'wanted_spot_list.html', {'wanted_spots': wanted_spots})



class CreateSchedule(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'plan/schedule.html')

    def post(self, request, *args, **kwargs):
        logger.debug("postメソッド呼び出し")
        schedule_range = request.POST.get('schedule_range')
        touristplan_name = request.POST.get('touristplan_name', '').strip()
        
        if schedule_range and ' to ' in schedule_range and touristplan_name:
            start_date, end_date = schedule_range.split(' to ')
            
            # データベースに保存
            TouristPlan.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                touristplan_name=touristplan_name
            )

            messages.success(request, 'プラン登録できました', extra_tags='touristplan')
            return redirect('travelapp:touristplan_list')
        
        return redirect('travelapp:schedule')


class TouristplanList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # ログインユーザーの旅行プランを取得
        queryset = TouristPlan.objects.filter(user=request.user)
        
        # GETパラメータ 'sort' によって並び替えを切り替え（デフォルトは-start_date順）
        sort_by = request.GET.get('sort', '-start_date')
        
        if sort_by == 'start_date':
            queryset = queryset.order_by('start_date')  # 開始日順 (昇順)
        elif sort_by == '-start_date':
            queryset = queryset.order_by('-start_date')  # 開始日順 (降順)
        elif sort_by == 'created_at':
            queryset = queryset.order_by('created_at')
        elif sort_by == '-created_at':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('start_date')  # デフォルトは開始日順

        context = {
            'touristplans': queryset,
            'sort_by': sort_by,
        }
        return render(request, 'plan/touristplan_list.html', context)


import logging

# ロガーの設定
class EditTouristPlanView(LoginRequiredMixin, View):
    def get(self, request, pk=None, *args, **kwargs):
        logger.debug("EditTouristPlanView.get called")

        plan = get_object_or_404(TouristPlan, pk=pk, user=request.user)
        logger.debug(f"Retrieved plan: {plan}")

        start_date = plan.start_date.strftime('%Y-%m-%d') if plan.start_date else ''
        end_date = plan.end_date.strftime('%Y-%m-%d') if plan.end_date else ''
        logger.debug(f"start_date: {start_date}, end_date: {end_date}")

        visit_date = []
        if start_date and end_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            visit_date = [
                (start_date_dt + timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range((end_date_dt - start_date_dt).days + 1)
            ]
        logger.debug(f"visit_date: {visit_date}")

        wanted_spots_queryset = request.user.wanted_spots.all()
        logger.debug(f"wanted_spots: {wanted_spots_queryset}")

        tourist_spot_id = request.GET.get('tourist_spot_id')
        logger.debug(f"tourist_spot_id: {tourist_spot_id}")

        if tourist_spot_id:
            tourist_spot = get_object_or_404(TouristSpot, id=tourist_spot_id)
            logger.debug(f"Found tourist_spot: {tourist_spot}")
        elif wanted_spots_queryset.exists():
            tourist_spot = wanted_spots_queryset.first().tourist_spot
            logger.debug(f"Selected tourist_spot from wanted_spots: {tourist_spot}")
        else:
            tourist_spot = None
            logger.debug("No tourist_spot selected.")

        stay_time_avg = (
            UserReview.objects.filter(tourist_spot=tourist_spot)
            .aggregate(Avg('stay_time_min'))['stay_time_min__avg']
            if tourist_spot else 0
        )
        stay_time_avg = stay_time_avg if stay_time_avg is not None else 0
        logger.debug(f"stay_time_avg: {stay_time_avg}")
        stay_time_hours = int(stay_time_avg) // 60
        stay_time_minutes = int(stay_time_avg) % 60
        logger.debug(f"stay_time_hours: {stay_time_hours}, stay_time_minutes: {stay_time_minutes}")

        tourist_spots_info = []
        for spot in wanted_spots_queryset:
            spot_data = spot.tourist_spot
            staytime = (
                UserReview.objects.filter(tourist_spot=spot_data)
                .aggregate(Avg('stay_time_min'))['stay_time_min__avg'] or 0
            )
            spot_data_dict = {
                'id': spot_data.id,
                'spot_name': spot_data.spot_name,
                'picture': spot_data.picture.url if spot_data.picture else None,
                'category': spot_data.get_category_display(),
                'prefecture': spot_data.get_prefecture_display(),
                'address': spot_data.address,
                'staytime_average': staytime,
                'staytime_hours': int(staytime) // 60,
                'staytime_minutes': int(staytime) % 60,
                'lat': spot_data.latitude,
                'lng': spot_data.longitude,
            }
            tourist_spots_info.append(spot_data_dict)
        logger.debug(f"tourist_spots_info: {tourist_spots_info}")

        google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

        selected_spots_info = []
        for ps in plan.tourist_spots.all():
            ts = ps.tourist_spot
            staytime = (
                UserReview.objects.filter(tourist_spot=ts)
                .aggregate(Avg('stay_time_min'))['stay_time_min__avg'] or 0
            )
            selected_spots_info.append({
                'id': ts.id,
                'visit_date': ps.visit_date.strftime('%Y-%m-%d') if ps.visit_date else '',
                'spot_name': ts.spot_name,
                'picture': ts.picture.url if ts.picture else None,
                'prefecture': ts.get_prefecture_display(),
                'address': ts.address,
                'lat': ts.latitude,
                'lng': ts.longitude,
                'staytime_hours': int(staytime) // 60,
                'staytime_minutes': int(staytime) % 60,
            })
        selected_spot_names = [spot['spot_name'] for spot in selected_spots_info]
        logger.debug(f"selected_spots_info: {selected_spots_info}")
        logger.debug(f"selected_spot_names: {selected_spot_names}")

        formset = TouristPlanSpotFormSet(queryset=TouristPlan_Spot.objects.filter(tourist_plan=plan))

        context = {
            'plan': plan,
            'visit_date': visit_date,
            'wanted_spots': tourist_spots_info,
            'selected_spots': selected_spots_info,
            'selected_spot_names': selected_spot_names,
            'tourist_spot': tourist_spot,
            'stay_time_avg': stay_time_avg,
            'stay_time_hours': stay_time_hours,
            'stay_time_minutes': stay_time_minutes,
            'formset': formset,
            'google_maps_api_key': google_maps_api_key,
        }

        return render(request, 'plan/edit_touristplan.html', context)


    def post(self, request, pk=None, *args, **kwargs):
        logger.debug("EditTouristPlanView.post called")

        plan = get_object_or_404(TouristPlan, pk=pk, user=request.user)
        logger.debug(f"Retrieved plan for POST: {plan}")

        # formsetは使わずに選択された観光地を処理
        selected_spot_ids = request.POST.getlist('selected_spot_ids')  # 選択された観光地のIDリスト
        selected_visit_dates = request.POST.getlist('visit_dates')  # 各観光地の訪問日リスト

        # 既存のTouristPlan_Spotインスタンスを削除（必要に応じて）
        plan.tourist_spots.all().delete()

        # 観光地を順番通りに保存
        for order, (spot_id, visit_date) in enumerate(zip(selected_spot_ids, selected_visit_dates), start=1):
            tourist_spot = get_object_or_404(TouristSpot, id=spot_id)  # 観光スポットを取得
            # TouristPlan_Spotを新規作成
            tourist_plan_spot = TouristPlan_Spot(
                tourist_plan=plan,
                tourist_spot=tourist_spot,
                visit_date=visit_date,
                order=order  # 順番を設定
            )
            tourist_plan_spot.save()  # 保存

        logger.debug(f"Saved TouristPlan_Spot: {tourist_plan_spot}")

        messages.success(request, 'プラン登録できました', extra_tags='touristplan')
        return redirect('travelapp:touristplan_list')




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def update_touristplan_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            for item in data["order"]:
                spot = TouristPlan_Spot.objects.get(id=item["id"])
                spot.order = item["position"]
                spot.save()
            return JsonResponse({"message": "順番を更新しました"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "無効なリクエスト"}, status=400)
    

def delete_touristspot(request, pk):
    tourist_spot = get_object_or_404(TouristSpot, pk=pk)

    if request.method == "POST":
        # 画像ファイルの削除
        if tourist_spot.picture:
            picture_path = tourist_spot.picture.path
            if os.path.isfile(picture_path):
                os.remove(picture_path)

        # データベースから削除
        tourist_spot.delete()

        return redirect('travelapp:home')  # ホームにリダイレクト（必要に応じて変更）
    