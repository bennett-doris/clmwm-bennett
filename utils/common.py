# 用来存储类似的公共方法

import json
import requests
from django.conf import settings
from django.shortcuts import render,redirect

def get_lng_lat(address):
    """降低至解析为经纬度"""

    url = settings.BAIDU_LNG_LAT_URL
    params = {
        'address':address,
        'output':'json',
        'ak':settings.BAIDU_AK
    }
    res = requests.get(url,params=params)
    res.encoding = 'utf-8'
    temp = json.loads(res.text)
    lat = temp['result']['location']['lat']
    lng = temp['result']['location']['lng']

    return {'lat':lat,'lng':lng}        # 纬度 latitude   经度 longitude

def get_distance_duration(origin,destination):
    """计算起点到终点距离，时间，以及配送费"""
    url = settings.BAIDU_RIDING_URL
    ak = settings.BAIDU_AK
    # 起点经纬度，格式：纬度，经度；小数点后不超过六位
    origin_lng = str(origin['lng'])
    origin_lat = str(origin['lat'])
    destination_lng = str(destination['lng'])
    destination_lat = str(destination['lat'])
    params = {
        'origin':origin_lat+','+origin_lng,
        'destination':destination_lat+','+destination_lng,
        'ak':ak
    }
    res = requests.get(url,params = params)
    res.encoding = 'utf-8'
    temp = json.loads(res.text)
    distance =temp['result']['routes'][0]['distance']
    duration = temp['result']['routes'][0]['duration']
    return {'distance':distance,'duration':duration}

def verify_exist(request,name,value):
    """验证是否重复"""
    from apps.user.models import User
    try:
        user = User.objects.get(**{name:value})
    except User.DoesNotExist:
        user = None
    if user:
        return True
    else:
        return False

def goods_item(item):
    '''获取商品图片'''
    from collections import  Iterable
    from apps.goods.models import GoodsImage

    # 判断是否为可迭代对象
    if isinstance(item,Iterable):
        for info in item:
            image = GoodsImage.objects.get(sku_id=info.id).image
            info.image = image
    else:
        item.image = GoodsImage.objects.get(sku_id=item.id).image
    return item

def shop_is_new(shop):
    '''判断店铺是否为新店'''
    import datetime
    from collections import Iterable

    # 获取30天前的时间
    one_month_ago = (datetime.datetime.now()-datetime.timedelta(30)).replace(tzinfo=None)

    # 判断传入的数据是否可以遍历
    if isinstance(shop,Iterable):
        for info in shop:
            if info.create_time.replace(tzinfo = None) > one_month_ago:
                info.shop_score = '新店'
            info.create_time = info.create_time.strftime('%Y-%m-%d')
    else:
        if shop.create_time.replace(tzinfo = None) > one_month_ago:
            shop.shop_score = '新店'
        shop.create_time = shop.create_time.strftime('%Y-%m-%d')

    return shop

def page_item(info,page,page_number):
    '''控制分页'''
    from django.core.paginator import Paginator

    # 对数据进行分页
    paginator = Paginator(info,page_number)

    # 获取第Page 页的内容
    try:
        page = int(page)
    except Exception as e:
        page = 1
    if page > paginator.num_pages:
        page = 1

    # 获取第page页的Page实例对象
    info = paginator.page(page)

    # 进行页码控制，最多显示5个页码
    # 总页数小于5页，页面上显示所有页码
    # 如果当前页是前3页，显示1—5页
    # 如果但前额是后3页，显示后5页
    # 其他情况，显示当前页的前2页，当前页，当前页的后2页
    num_pages = paginator.num_pages
    if num_pages < 5:
        pages = range(1,num_pages + 1)
    elif page <=3:
        pages = range(1,6)
    elif num_pages - page <= 2:
        pages = range(num_pages - 4,num_pages + 1)
    else:
        pages = range(num_pages - 2,page + 3)

    # 整合数据
    context = {'info':info,'pages':pages}
    return context


def for_item(item):
    '''获取店铺图片'''
    from collections import Iterable
    from apps.user.models import ShopImage

    # 判断是否为可迭代对象
    if isinstance(item,Iterable):
        for info in item:
            image = ShopImage.objects.get(shop_id=info.id).image
            info.shop_image = image
    else:
        item.shop_image = ShopImage.objects.get(shop_id=item.id).image

    return item

def calculate_distance_duration(shop,user,address_id = None):
    '''调用百度地图计算配送费、时间'''
    from collections import Iterable
    from apps.user.models import Address

    # 判断传入数据是否可以遍历
    if isinstance(shop,Iterable):
        for info in shop:
            if address_id is None:
                address_shop = Address.objects.get(is_default=True,user = info.user)
                address_user = Address.objects.get(is_default=True,user = user)
            else:
                address_shop = Address.objects.get(is_default=True,user = info.user)
                address_user = Address.objects.get( id=address_id)
            distance_duration = get_distance_duration({'lat':address_shop.lat,'lng':address_shop.lng},
                                                      {'lat':address_user.lat,'lng':address_user.lng})
            # 得出距离和时间
            info.send_price = int(distance_duration['distance']/1000)
            info.duration = int(distance_duration['duration']/60)
    else:
        if address_id is None:
            address_shop = Address.objects.get(is_default=True, user=shop.user)
            address_user = Address.objects.get(is_default=True, user=user)
        else:
            address_shop = Address.objects.get(is_default=True, user=shop.user)
            address_user = Address.objects.get(id=address_id)
        distance_duration = get_distance_duration({'lat': address_shop.lat, 'lng': address_shop.lng},
                                                  {'lat': address_user.lat, 'lng': address_user.lng})
        # 得出距离和时间
        shop.send_price = int(distance_duration['distance'] / 1000)
        shop.duration = int(distance_duration['duration'] / 60)

    return shop


def get_comment_confusion(score_begin,score_end,shop,page):
    '''获取各种评价的公共方法'''
    from collections import  Iterable
    from apps.order.models import OrderInfo,CommentInage,OrderGoods
    from apps.user.models import UserImage

    order_info = OrderInfo.objects.filter(score_get = score_begin,score_lt = score_end,
                                          shop=shop,order_status=7).order_by('-create_time')

    get_image(order_info,UserImage,'user_id')
    get_image(order_info,CommentInage,'order_id',foreign_key = True)

    if isinstance(order_info,Iterable):
        for order in order_info:
            goods = OrderGoods.objects.get(order=order)
            order.goods = goods
    else:
        goods = OrderGoods.objects.get(order=order_info)
        order_info.goods = goods

    # 将数据进行分页
    context = page_item(order_info,page,4)
    return context

def get_image(item,object_name,field,foreign_key = False):
    """获取图片"""
    from collections import Iterable

    # 判断是否可迭代
    if isinstance(item,Iterable):
        for info in item:
            '''订单表无id特殊处理'''
            if not foreign_key and not hasattr(info,'id'):
                info = info.user
            elif not hasattr(info,'id'):
                info.id = info.order_id

            try:
                image = object_name.objects.get(**{field:info.id}).image
                info.image = image
            except Exception as e:
                image_list = object_name.objects.filter(**{field:info.id})
                info.image_list = image_list

    else:
        # 订单表特殊处理
        if not foreign_key and not hasattr(item,'id'):
            item = item.user
        elif not hasattr(item,'id'):
            item.id = item.order_id
        try:
            image = object_name.objects.get(**{field:item.id}).image
            item.image = image
        except Exception as e:
            image_list = object_name.objects.filter(**{field:item.id})
            item.image_list = image_list

    return item

def good_rate(shop):
    '''计算好评率'''
    from apps.order.models import OrderInfo
    a_count = OrderInfo.objects.filter(score__gte=6,score__lt=10,shop = shop,
                                       order_status=7).count()
    total_count = OrderInfo.objects.filter(shop=shop,order_status=7).count()
    if total_count != 0:
        rate = '{:.2%}'.format(a_count/total_count)
    else:
        rate = '0.00%'

    return rate


def order_detail(order_status,page,shop):
    '''
    根据状态码查询明细
    以字典的形式返回
    order_info 与 order_goods
    '''
    from collections import Iterable
    from django.db.models import F,Q
    from apps.order.models import OrderInfo,OrderGoods

    if isinstance(order_status,Iterable):
        order_info = page_item(
            OrderInfo.objects.filter(
                Q(order_status=order_status[0],shop=shop) |
                Q(order_status=order_status[1],shop=shop))
                .order_by('-update_time'),page,10)
        goods = OrderGoods.objects.filter(
            order_info = OrderInfo.objects.values_list('order_id').filter(
                Q(order_status=order_status[0],shop=shop) |
                Q(order_status = order_status[1],shop=shop)
            ).order_by('-update_time'))
        order_info.update({'goods':goods})
    else:
        order_info = page_item(
            OrderInfo.objects.filter(
               order_status=order_status, shop=shop)
                .order_by('-update_time'), page, 10)
        goods = OrderGoods.objects.filter(
            order_info=OrderInfo.objects.values_list('order_id').filter(
                order_status=order_status, shop=shop)
            .order_by('-update_time'))
        order_info.update({'goods': goods})

    return order_info
