from django.urls import path,re_path
from apps.cart.views import  VmStartView,save_address


urlpatterns = [
    path('wm_start/',VmStartView.as_view(),name='vm_start'),
    path('address/',save_address,name='address'),
]