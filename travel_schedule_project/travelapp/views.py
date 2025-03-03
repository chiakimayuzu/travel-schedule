from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView


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
        if form.is_valid():
            # フォームが有効ならば、ログイン処理などを追加する
            return redirect(self.success_url)  # 成功した場合は指定されたURLにリダイレクト
        return render(request, self.template_name, {'form': form})  # フォームにエラーがあれば再表示



class UserLogoutView(View):
    pass


class RegistAccountView(FormView):
    model = User
    template_name = 'regist_account.html'
    form_class = RegistAccountForm
    success_url = reverse_lazy('travelapp:login')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

def regist_view(request):
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