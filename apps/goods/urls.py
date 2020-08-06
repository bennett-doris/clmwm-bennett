from django.urls import path,re_path
from apps.goods.views import index,VmIndexView,ShopDetailView,MySearchView,sj_index

app_name = 'goods'

urlpatterns = [
    path('find/',MySearchView.as_view(),name='haystack'),
    re_path(r'^goods/(?P<goods_id>\d+)/(?P<a_page>\d+)/(?P<b_page>\d+)/(?P<c_page>\d+)$',
            ShopDetailView.as_view(),name='shop_detail'),
    path('',index,name='index'),      # 买家首页
    re_path(r'^wm_index/(?P<code>[0,4])/(?P<page>\d+)/$',VmIndexView.as_view(),name='wm_index'),      #店铺列表
    path('sj_index/',sj_index,name='sj_index')
]