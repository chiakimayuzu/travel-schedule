from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from .forms import ChangeEmailForm, PasswordChangeForm, RegistAccountForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from .forms import TouristSpotForm
from .models import Keyword, TouristSpot, TouristSpotKeyword
from django.shortcuts import render, redirect
from .forms import TouristSpotForm
from .models import Keyword, TouristSpotKeyword
from geopy.geocoders import GoogleV3
from django.conf import settings
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
        return render(request, "account/user_login.html", {"form": form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # form.user を使ってユーザー情報を取得
            user = form.user
            login(request, user)
            return redirect("travelapp:home")
        return render(request, "account/user_login.html", {"form": form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)  # GET でもログアウト処理を実行
        return redirect('travelapp:home')  # 直接ホームにリダイレクト

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('travelapp:home')



def check_username(request): #入力されたusernameが既に存在するかを確認
        username = request.GET.get('username')  # フォームの入力値を取得
        exists = User.objects.filter(username=username).exists()  # usernameがすでに存在するか確認
        return JsonResponse({'exists':exists})  # exists が True ならusernameが存在、エラー表示


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(user=request.user, data=request.POST)
        if form.is_valid():
            # メールアドレスの更新処理
            request.user.email = form.cleaned_data['new_email']
            request.user.save()
            # 成功メッセージを追加してリダイレクト
            messages.success(request, 'メールアドレスが更新されました。')
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
            messages.success(request, 'パスワードが更新されました。') # 成功メッセージが同じページに表示されるようにします
            return redirect('travelapp:change_password')  
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})


class PortfolioView(View):
    def get(self, request):
        return render(request, "portfolio.html")

def homeview(request):
    return render(request, 'home.html')

def regist_touristspot(request):
    if request.method == "POST":
        form = TouristSpotForm(request.POST)
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

            tourist_spot.save()  # ★保存
            messages.success(request, '観光地登録できました')
            return redirect('travelapp:regist_touristspot.html')
        
            # ★キーワードの保存処理（新しいキーワードをDBに登録）
            keywords_text = form.cleaned_data.get("keywords")
            if keywords_text:
                # もしカンマ区切りで複数キーワードを入力する場合はリストに分割
                keywords_list = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                for keyword_text in keywords_text:
                    keyword, created = Keyword.objects.get_or_create(keyword=keyword_text)
                    TouristSpotKeyword.objects.create(tourist_spot=tourist_spot, keyword=keyword)
            
            tourist_spot.save()  # 保存する
            messages.success(request, '観光地登録できました') # 成功メッセージが同じページに表示されるようにします
            return redirect('travelapp:regist_touristspot.html')

    else:
        form = TouristSpotForm()

    return render(request, 'regist_touristspot.html', {'form': form})

def check_dupe_tourist_spot(request):
    spot_name = request.GET.get('spot_name', '').strip()
    address = request.GET.get('address', '').strip()
     #strip()があることで空白があってもスルーしてエラー発生させてくれる

    return JsonResponse({
        'spot_name_exists': TouristSpot.objects.filter(spot_name=spot_name).exists() if spot_name else False,
        'address_exists': TouristSpot.objects.filter(address=address).exists() if address else False
    })