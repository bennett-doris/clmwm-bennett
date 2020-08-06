from django.urls import path, re_path
from apps.user.views import RegisterView,UserActivate,ShopRegister,find_type,LoginView

app_name = 'user'
urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),       # 注册
    re_path(r'^activate/(?P<token>.*)$',UserActivate.as_view(),name='activate'),
    path('sj_register/',ShopRegister.as_view(),name='sj_register'),      # 店铺注册
    re_path(r'^type_detail$',find_type,name='type_detail'),
    path('login/',LoginView.as_view(),name='login'),     # 登录

]