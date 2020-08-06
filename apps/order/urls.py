from django.urls import path,re_path
from apps.order.views import OrderGenerateView,OrderPayView,CheckPayView,OrderBuySuccessView,QueryOrderVIew,GoCommentView


urlpatterns = [
    path('generate/',OrderGenerateView.as_view(),name='generate'),
    path('pay/',OrderPayView.as_view(),name='pay'),
    path('check/',CheckPayView.as_view(),name='check'),
    path('success/<order_id>',OrderBuySuccessView.as_view(),name='success'),
    path('query/<page>',QueryOrderVIew.as_view(),name='query'),
    path('go_comment/<order_id>',GoCommentView.as_view(),name='go_comment'),
]