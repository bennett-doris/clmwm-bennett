from django.http import JsonResponse
from django.shortcuts import render,redirect,reverse

# Create your views here.
from django.views import View
from apps.goods.models import GoodsSKU,Goods
from apps.user.models import Shop,User,Address
from utils.common import calculate_distance_duration,get_lng_lat

class VmStartView(View):
    '''订单确认'''

    def get(self,request):
        array_id = request.GET.get('cm1').split(',')
        array_count = request.GET.get('cm2').split(',')
        if len(array_id) != len(array_count):
            return redirect(reverse('goods:vm_index',{'errmsg':'数据错误'}))

        sku_info = GoodsSKU.objects.filter(id__in =array_id)

        # 遍历出所有的商品
        flag,total,total_goods = 0,0,0
        for sku in sku_info:
            sku_unite = array_count[flag]
            total_goods = total_goods + (sku.price+int(sku.pack))*int(sku.unite)
            goods = Goods.objects.get(id = sku.goods_id)
            shop = Shop.objects.get(id = goods.shop_id)
            flag += 1

        if request.user.id:
            print('该用户的id为：%s' %request.user.id)
        else:
            return redirect(reverse('user:login'))

        user = User.objects.get(id = request.user.id)

        # 计算运费
        distance = calculate_distance_duration(shop,user)

        # 总支付价格
        total = total_goods + int(distance.send_price)

        # 设置顺序
        address_info = Address.objects.order_by('-is_default').filter(user_id = request.user.id)

        # 整合数据
        context = {
            'sku_info':sku_info,
            'total_goods':total_goods,
            'total':total,
            'shop':shop,
            'user':user,
            'address_info':address_info,
        }
        return render(request,'wm_plaorder.html',context)

    def post(self):
        pass


def save_address(request):
    '''处理新增地址'''
    try:
        user = User.objects.get(id = request.user.id)
    except User.DoesNotExist:
        return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录！'})

    receiver = request.GET.get('receiver')
    addr_region = request.GET.get('region')
    addr_factor = request.GET.get('addr')
    phone = request.GET.get('phone')
    default = request.GET.get('default')

    # 校验数据
    if not all([receiver,addr_factor,addr_region,phone,default]):
        return JsonResponse({'res':1,'errmsg':'缺少相关数据'})

    # 整合地址数据
    addr = addr_region + addr_factor

    if int(default) > 0:
        default = True
        # 查询出默认地址，设为非默认状态
        address_user = Address.objects.get(is_default=True,user=user)
        address_user.is_default = False
        address_user.save()
    else:
        default = False

    # 调用方法，获取经纬度
    lat_lng = get_lng_lat(addr)
    lat = lat_lng['lat']
    lng = lat_lng['lng']

    # 地址表新增数据
    address = Address(user = user,receiver = receiver,phone = phone,addr = addr,
                      is_default=default,lat=lat,lng=lng)
    address.save()

    return JsonResponse({'res':2,'errmsg':'保存成功'})
