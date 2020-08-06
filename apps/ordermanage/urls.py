from django.urls import path,re_path
from apps.ordermanage.views import SjOrderView,OrderReceive,OrderRefuse,status

urlpatterns = [
    re_path(r'^sj_order/(?P<page>\d+)',SjOrderView.as_view(),name='sj_order'),
    path('receive/<order_status>/<order_id>',OrderReceive.as_view(),name='receive'),   # 商家接收订单
    path('refuse/<order_id>',OrderRefuse.as_view(),name='refuse'),      # 商家拒绝订单
    path('status/',status,name='status')
]