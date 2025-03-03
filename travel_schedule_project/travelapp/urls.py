from django.urls import path
from travelapp import views
from .views import (
    RegistAccountView, HomeView,LoginView,regist_view)



app_name = 'travelapp'
urlpatterns = [
    path('user_login/',LoginView.as_view(),name='login'),
    path('regist_account/',RegistAccountView.as_view(),name='regist_account'),
    path('home/',HomeView.as_view(),name='home'),
    path('ajax/regist_account/', regist_view, name='regist_ajax'), 
]
