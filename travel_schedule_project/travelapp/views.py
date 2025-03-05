from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import ChangeEmailForm, PasswordChangeForm, RegistAccountForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
# Create your views here.

class LoginView(View):
    template_name = 'account/user_login.html'
    authentication_form = UserLoginForm
    success_url = reverse_lazy('travelapp:home')  # ここでURLを解決

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
            

            #★ここも機能していない★
            if user is not None:  # 認証に成功した場合
                login(request, user)  # ログイン処理
                next_url = request.GET.get('next', self.success_url)
                print(f"Redirecting to: {next_url}")  # ログを確認
                return redirect(next_url)  # リダイレクト
            else:
                form.add_error(None, "認証に失敗しました")  # 認証失敗時のエラーメッセージ
        return render(request, self.template_name, {'form': form})  # フォームにエラーがあれば再表示

class UserLogoutView(View):
    pass


class RegistAccountView(CreateView):
    model = User
    template_name = 'account/regist_account.html'
    form_class = RegistAccountForm
    success_url = reverse_lazy('travelapp:login')

    def form_valid(self, form):
        # フォームが有効な場合、保存してからリダイレクト
        response = super().form_valid(form)
        return response  # success_url にリダイレクトされます
    
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)


def check_username(request): #入力されたusernameが既に存在するかを確認
        username = request.GET.get('username')  # フォームの入力値を取得
        exists = User.objects.filter(username=username).exists()  # usernameがすでに存在するか確認
        return JsonResponse({'exists':exists})  # exists が True ならusernameが存在、エラー表示


def check_password(request): #入力PWとcomfirm PWが同一かチェック
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

#@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(user=request.user, data=request.POST)
        if form.is_valid():
            # メールアドレスの更新処理
            request.user.email = form.cleaned_data['new_email']
            request.user.save()
            # 成功メッセージを追加してリダイレクト
            messages.success(request, 'メールアドレスが更新されました。')
            return redirect('email_change')  # プロフィールページなどの適切なリダイレクト先に変更してください
    else:
        form = ChangeEmailForm(user=request.user)
    
    return render(request, 'account/change_email.html', {'form': form})



#@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # パスワード変更後もログイン状態を保持
            messages.success(request, 'パスワードが更新されました。')
            return redirect('password_change')  # 成功メッセージが同じページに表示されるようにします
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})



class HomeView(View):
    template_name = 'home.html'

