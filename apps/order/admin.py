from django.contrib import admin
from .models import *
# Register your models here.

# 将模型注册到后台
# admin.site.register(OrderInfo)

# 修改title 和 header
admin.site.site_title = '吃了么-后台管理'
admin.site.site_header = '吃了么'

# 自定义OrderAdmin类并继承ModelAdmin
@admin.register(OrderInfo)
class OrderAdmin(admin.ModelAdmin):
    # 设置显示的字段
    list_display = ['order_id','user','addr','shop','comment']
    # 设置搜索字段
    search_fields = ['order_id','user__id','addr__id','shop__id','comment']
    # 设置过滤器，如有外键应使用双下划线连接连个模型的字段
    list_filter = ['order_id']
    # 设置排序方式
    ordering = ['-order_id']
    # 设置时间选择器
    # date_hierarchy = Field
    # 在添加数据时，设置可添加数据的字段
    fields = ['order_status','remarks','score','taxpayer_number','invoice_head']
    # 设置可读字段，在修改和添加数据时使其无法设置
    readonly_fields = ['order_id','user','addr','shop']

    # 重写get_readonly 函数，设置超级用户和普通用户的权限
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = []
        return self.readonly_fields
    # 添加自定义字段，在属性list_display 添加自定义字段total_price
    list_display.append('total_price')

    # 根据当前用户名设置访问权限
    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(id__lt = 6)