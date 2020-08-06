"""clmwm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include,re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include(('apps.user.urls','apps.user'),namespace='user')),  # 用户模块
    path('cart/',include(('apps.cart.urls','apps.cart'),namespace='cart')),
    path('order/',include(('apps.order.urls','apps.order'), namespace='order')),
    re_path(r'^',include(('apps.goods.urls','apps.goods'),namespace='goods')),          # 商品模块，主页
    path('comment/',include(('apps.comment.urls','apps.comment'),namespace='comment')),
    path('ordermanage/',include(('apps.ordermanage.urls','apps.ordermanage'),namespace='ordermanage')),
    path('goodsmanage/',include(('apps.goodsmanage.urls','apps.goodsmanage'),namespace='goodsmanage')),
    path('commentmanage/',include(('apps.commentmanage.urls','apps.commentmanage'),namespace='commentmanage'))
]

# 仅在debug模式下加载模块
if settings.DEBUG:
    urlpatterns = [
        path('__debug__/',include(debug_toolbar.urls)),
    ]+urlpatterns
