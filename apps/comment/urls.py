from django.urls import  path,re_path
from apps.comment.views import new

urlpatterns = [
    path('order/',new,name='order'),
]