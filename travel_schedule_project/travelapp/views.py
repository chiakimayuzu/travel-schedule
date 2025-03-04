from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistAccountForm, UserLoginForm

# Create your views here.

class LoginView(View):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        form = self.authentication_form()  # フォームのインスタンスを作成
        return render(request, self.template_name, {'form': form})  # フォームをテンプレートに渡す

    def post(self, request, *args, **kwargs):
        form = self.authentication_form(request.POST)  # POSTデータを使ってフォームを作成
        if form.is_valid():  # フォームが有効なら
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            
            # ユーザーの認証を行う
            user = authenticate(request, email=email, password=password)
            
            if user is not None:  # 認証に成功した場合
                login(request, user)  # ログイン処理
                return redirect(self.success_url)  # 成功した場合、指定されたURLにリダイレクト
            else:
                form.add_error(None, "認証に失敗しました")  # 認証失敗時のエラーメッセージ
        return render(request, self.template_name, {'form': form})  # フォームにエラーがあれば再表示


class UserLogoutView(View):
    pass


class RegistAccountView(CreateView):
    model = User
    template_name = 'regist_account.html'
    form_class = RegistAccountForm
    success_url = reverse_lazy('travelapp:login')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def check_username(request): #入力されたusernameが既に存在するかを確認
        username = request.GET.get('username')  # フォームの入力値を取得
        exists = User.objects.filter(username=username).exists()  # usernameがすでに存在するか確認
        return JsonResponse({'exists':exists})  # exists が True ならusernameが存在、エラー表示


def regist_view(request): #入力PWとcomfirm PWが同一かチェック
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        form = RegistAccountForm(request.POST)
        if form.is_valid():
            # バリデーション成功時の処理（例: ユーザー登録処理）
            return JsonResponse({'success': True})

        # バリデーションエラーがある場合、エラー内容をJSONで返す
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors})

    else:
        form = RegistAccountForm()

    return render(request, 'regist_form.html', {'form': form})

class HomeView(View):
    template_name = 'home.html'