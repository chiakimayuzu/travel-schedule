from django.urls import path
from .views import (
    CreateSchedule, EditTouristPlanView, ModalSearchTouristSpotView, RegistAccountView, 
    TouristSpotSearchView, TouristplanList, check_username, create_review, create_touristplan, edit_my_review, home,
    LoginView,LogoutView,change_password,change_email,
    PortfolioView, my_review_detail, my_review_list,regist_touristspot,check_dupe_tourist_spot,
    detail_touristspot,edit_touristspot, review_list, wanted_spot, wanted_spot_list, 
    )   
# from .views import ModalWantedSpotView


app_name = 'travelapp'
urlpatterns = [
    path('user_login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('regist_account/',RegistAccountView.as_view(),name='regist_account'),
    path('check_username/',check_username,name='check_username'),
    path('home/',home,name='home'),
    path('search_touristspot/', TouristSpotSearchView.as_view(), name='search_touristspot'), 
    path('change_email/', change_email, name='change_email'),#メールアドレス変更view
    path('change_password/', change_password, name='change_password'),  # パスワード変更view
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('regist_touristspot/', regist_touristspot, name='regist_touristspot'),
    path('check_dupe_tourist_spot/', check_dupe_tourist_spot, name='check_dupe_tourist_spot'),
    path('detail_touristspot/<int:pk>/', detail_touristspot, name='detail_touristspot'),
    path('edit_touristspot/<int:pk>/', edit_touristspot, name='edit_touristspot'),
    path('create_review/<int:pk>/', create_review, name='create_review'),
    path('edit_my_review/<int:pk>/', edit_my_review, name='edit_my_review'),
    path('my_reviews_list/', my_review_list, name='my_review_list'),    
    path('my_reviews_detail/<int:review_id>', my_review_detail, name='my_review_detail'),    
    path('review_list/<int:pk>/', review_list, name='review_list'),
    path('wanted_spot/<int:tourist_spot_id>/', wanted_spot, name='wanted_spot'),  # 行きたいリストに追加
    path('wanted_spot_list/', wanted_spot_list, name='wanted_spot_list'),  # 行きたいリスト
    
    path('create_touristplan/', create_touristplan, name='create_touristplan'),
    path('schedule/', CreateSchedule.as_view(), name='schedule'),
    # 観光地検索モーダル用URL
    path('modal_search_touristspot/', ModalSearchTouristSpotView.as_view(), name='modal_search_touristspot'),

    path('touristplan_list/', TouristplanList.as_view(), name='touristplan_list'),
    path('edit_touristplan/<int:pk>/', EditTouristPlanView.as_view(), name='edit_touristplan'),
    # path('modal_wanted_spot/<int:plan_id>/<str:visit_date>/', ModalWantedSpotView.as_view(), name='modal_wanted_spot'),
    # path('add_to_visit_date/<int:plan_id>/<str:visit_date>/', AddToVisitDateView.as_view(), name='add_to_visit_date'),
    ]
