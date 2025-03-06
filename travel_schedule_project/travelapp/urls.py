from django.urls import path
from .views import (
    RegistAccountView, homeview,LoginView,LogoutView,change_password,change_email)



app_name = 'travelapp'
urlpatterns = [
    path('user_login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('regist_account/',RegistAccountView.as_view(),name='regist_account'),
    path('home/',homeview,name='home'),
    path('change_email/', change_email, name='change_email'),#メールアドレス変更view
    path('change_password/', change_password, name='change_password'),  # パスワード変更view
    ]
