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
            messages.success(request, 'パスワードが更新されました。')
            return redirect('travelapp:change_password')  # 成功メッセージが同じページに表示されるようにします
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
            tourist_spot.save()

            # ★キーワードの保存処理（新しいキーワードをDBに登録）
            keywords_text = form.cleaned_data.get("keywords")
            for keyword_text in keywords_text:
                keyword, created = Keyword.objects.get_or_create(keyword=keyword_text)
                TouristSpotKeyword.objects.create(tourist_spot=tourist_spot, keyword=keyword)

            return redirect('success_page')

    else:
        form = TouristSpotForm()

    return render(request, 'regist_touristspot.html', {'form': form})