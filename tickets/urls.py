from django.urls import path
from . import views
from .views import (
    get_theaters, get_movies, get_dates, get_sessions,
    get_seats_for_showtime, register_view,login_view,logout_view
)

app_name = 'tickets'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('api/movies/', views.get_movies_json, name='get_movies_json'),
    # path('select_tickets/<int:showtime_id>/', views.select_tickets, name='select_tickets'),
    path('openNote/', views.open_note, name='open_note'),
    path('openInfo/', views.open_info, name='open_info'),
    # 先使用模擬
    path('select_tickets/<int:showtime_id>/', views.select_tickets, name='select_tickets'),
    #path('select_tickets/', views.select_tickets, name='select_tickets'),
    
    # 加入註冊頁
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'), 
    path('logout/', logout_view, name='logout'), 
    
    # 會員驗證
    path("verify/<token>/",views.verifyEmail,name="verifyEmail"),
    # 會員驗證碼過期,再次驗證
    path("resendVerify/",views.resendVerify,name="resendVerify"),
    # 會員資料
    path("member_data/",views.member_data,name="member_data"),
    # 忘記密碼
    path("forgetPassword/",views.forgetPassword,name="forgetPassword"),
    path("reset_password/",views.reset_password,name="reset_password"),
    path("change_password/",views.change_password,name="change_password"),
    
    # 座位選擇
    path('select_seats/<int:showtime_id>/', views.select_seats, name='select_seats'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('create-order/', views.create_order, name='create_order'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my_orders/', views.my_orders, name='my_orders'),
         
    # API
    
    path('api/seats/<int:showtime_id>/', get_seats_for_showtime, name='get_seats'),
    path('api/theaters/', get_theaters, name='get_theaters'),
    path('api/movies/<int:theater_id>/', get_movies, name='get_movies'),
    path('api/dates/<int:movie_id>/', get_dates, name='get_dates'),
    path('api/sessions/<int:theater_id>/<int:movie_id>/<str:date>/', get_sessions, name='get_sessions'),
    path("api/select_seat/", views.select_seat_api, name="select_seat_api"),
    
    # 綠界支付頁面
    path("payment/<int:order_id>/",views.payment,name="payment"),
    
    # 會員首頁
    path("member_index/",views.member_index,name="member_index"),
    
    
]
