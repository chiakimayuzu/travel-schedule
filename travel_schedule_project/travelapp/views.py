from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from django.contrib.auth.models import User
from .forms import RegistAccountForm, UserLoginForm

# Create your views here.

class LoginView(View):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm
    success_url = reverse_lazy('home')

class UserLogoutView(View):
    pass


class RegistAccountView(CreateView):
    model = User
    template_name = 'regist_account.html'
    form_class = RegistAccountForm
    success_url = reverse_lazy('user_login')

def regist_view(request):
    if request.is_ajax() and request.method == "POST":
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