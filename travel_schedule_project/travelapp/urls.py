from django.urls import path
from .views import (
    RegistAccountView, create_review, edit_review, homeview,LoginView,LogoutView,change_password,change_email,
    PortfolioView, my_review_list,regist_touristspot,check_dupe_tourist_spot,
    detail_touristspot,edit_touristspot, 
    )   



app_name = 'travelapp'
urlpatterns = [
    path('user_login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('regist_account/',RegistAccountView.as_view(),name='regist_account'),
    path('home/',homeview,name='home'),
    path('change_email/', change_email, name='change_email'),#メールアドレス変更view
    path('change_password/', change_password, name='change_password'),  # パスワード変更view
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('regist_touristspot/', regist_touristspot, name='regist_touristspot'),
    path('check_dupe_tourist_spot/', check_dupe_tourist_spot, name='check_dupe_tourist_spot'),
    path('detail_touristspot/<int:pk>/', detail_touristspot, name='detail_touristspot'),
    path('edit_touristspot/<int:pk>/', edit_touristspot, name='edit_touristspot'),
    path('create_review/<int:pk>/', create_review, name='create_review'),
    path('edit_review/<int:pk>/', edit_review, name='edit_review'),
    path('my_reviews_list/', my_review_list, name='my_review_list'),    
    ]
