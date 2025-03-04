from django.urls import path
from .views import (
    RegistAccountView, HomeView,LoginView,check_username,check_password,change_password,change_email)



app_name = 'travelapp'
urlpatterns = [
    path('user_login/',LoginView.as_view(),name='login'),
    path('regist_account/',RegistAccountView.as_view(),name='regist_account'),
    path('home/',HomeView.as_view(),name='home'),
    path('check_password/', check_password, name='check_password'), #PWが入力・再入力が同一かチェック用
    path('check_username/', check_username, name='check_username'),  # ユーザーID重複チェック用
    path('change_email/', change_email, name='change_email'),#メールアドレス変更view
    path('change_password/', change_password, name='change_password'),  # パスワード変更view
    ]
