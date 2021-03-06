import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect,reverse
from apps.user.models import User,Shop,ShopTypeDetail
from apps.goods.models import GoodsType,GoodsSKU
from apps.order.models import OrderInfo,OrderGoods
from utils.common import for_item, shop_is_new, calculate_distance_duration, goods_item, get_comment_confusion, \
    good_rate

# Create your views here.
from django.views import View


def index_again(shop_info,user):
    '''处理买家首页，抽取公共方法'''
    # 为店铺插入图片
    for_item(shop_info)

    # 判断店铺是否为新店
    shop_is_new(shop_info)

    # 调用百度地图API计算配送费，时间
    calculate_distance_duration(shop_info,user)


def  index(request):
    '''买家首页'''
    if request.user.is_staff:
        # 判断是否为商家
        return redirect(reverse('goods:sj_index'))

    # 由于需要获取用户地址信息，所以必须为登录状态
    try:
        user = User.objects.get(id = request.user.id)
    except User.DoesNotExist:
        return redirect(reverse('user:login'))

    # 获取所有店铺，数字为店铺大类
    shop_info0 = index_again(Shop.objects.get(shop_type='0'),user)
    shop_info1 = index_again(Shop.objects.get(shop_type='1'), user)
    shop_info2 = index_again(Shop.objects.get(shop_type='2'), user)
    shop_info3 = index_again(Shop.objects.get(shop_type='3'), user)

    context = {
        'shop_info0':shop_info0,
        'shop_info1':shop_info1,
        'shop_info2':shop_info2,
        'shop_info3':shop_info3,
    }

    return render(request,'index.html',context)


class VmIndexView(View):
    '''店铺分类显示'''
    def get(self,request,code,page):
        try:
            user = User.objects.get(id = request.user.id)
        except User.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        type_info = None
        if code == '4':
            shop_info = Shop.objects.all()
        else:
            shop_info = Shop.objects.get(shop_type = code)
            if code == '0':
                type_info = ShopTypeDetail.objects.filter(type_code__contains='C')
            if code == '1':
                type_info = ShopTypeDetail.objects.filter(type_code__contains='W')

        # 获取店铺图片
        for_item(shop_info)

        # 计算配送费，时间
        calculate_distance_duration(shop_info,user)

        # 判断店铺是否为新店
        shop_is_new(shop_info)

        # 对数据进行分页
        # 第一个参数 分页的对象       第二个参数 每页的条数
        paginator = Paginator(shop_info,16)

        # 获取page页的内容

        # 处理页码出错的问题
        try:
            page = int(page)
        except Exception as e:
            page = 1

        # 判断是否超出总页数范围
        if page > paginator.num_pages:
            page = 1

        # 获取第page页的内容
        skus_page = paginator.page(page)

        # 进行页码的控制
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1,num_pages + 1)
        elif page <= 3:
            pages = range(1,6)
        elif num_pages - page >=2 :
            pages = range(num_pages - 4,num_pages + 1)
        else:
            pages = range(page - 2,page + 3)

        context = {'code':code,'type_info':type_info,'skus_page':skus_page,'pages':pages}
        return render(request,'wm_index.html',context)


class ShopDetailView(View):
    '''显示店铺详情页'''
    def get(self,request,goods_id,a_page,b_page,c_page):

        try:
            shop = Shop.objects.get(id = goods_id)
            for_item(shop)
        except Shop.DoesNotExist:
            return render(request,'wm_index.html',{'errmsg':'店铺不存在'})

        try:
            user = User.objects.get(id= request.user.id)
        except User.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录！'})

        # 获取店铺下所售商品的种类
        type_info = GoodsType.objects.get(shop_id = goods_id)

        # 获取该店铺所有商品
        sku_info = GoodsSKU.objects.get(goods_shop_id =goods_id)

        # 添加图片路径
        goods_item(sku_info)

        # 是否显示为新店
        shop_is_new(shop)

        # 调用百度地图计算配送费，时间
        calculate_distance_duration(shop,user)

        # 获取该店铺的好评
        order_info_a = get_comment_confusion(6,11,shop,a_page)

        # 获取该店铺的中评
        order_info_b = get_comment_confusion(3, 6, shop, b_page)

        # 获取该店铺的差评
        order_info_c = get_comment_confusion(0, 3, shop, c_page)

        rate = good_rate(shop)

        # 整合数据
        context = {
            'shop':shop,
            'sku_info':sku_info,
            'type_info':type_info,
            'rate':rate,
            'order_info_a':order_info_a,
            'order_info_b':order_info_b,
            'order_info_c':order_info_c,
        }
        return render(request,'wm_shop.html',context)


class MySearchView(View):
    # 模板文件
    template = 'search.html'

    # 重写响应方式，如果请求参数q为空，返回模型Shop的全部数据，否则根据参数q搜索相关数据
    def create_response(self):
        if not self.request.GET.get('q',''):
            show_all = True
            shop = Shop.objects.al()

            try:
                user = User.objects.get(id =self.request.user.id)
            except User.DoesNotExist:
                return render(self.request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录！'})

            # 获取店铺图片
            for_item(shop)

            # 计算配送费、时间
            calculate_distance_duration(shop,user)

            # 判断是否为新店：
            shop_is_new(shop)

            paginator = Paginator(shop,16)
            try:
                page = paginator.page(int(self.request.GET.get('page',1)))
            except PageNotAnInteger:
                # 如果参数不是整型
                page = paginator.page(1)
            except EmptyPage:
                # 用户访问的页数大于实际页数，则返回最后一页的数据
                page = paginator.page(paginator.num_pages)
            return render(self.request,self.template,locals())
        else:
            show_all = False
            qs = super(MySearchView,self).create_response()
            return qs


def sj_index(request):
    '''商家首页'''
    # 验证是否登录
    try:
        shop = Shop.objects.get(user_id = request.user.id)
    except Shop.DoesNotExist:
        return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

    today = datetime.datetime.now()
    today_str = today.replace(tzinfo=None).strftime('%Y-%m-%d')
    week_str = (datetime.datetime.now() - datetime.timedelta(today.weekday())).\
        replace(tzinfo=None).strftime('%Y-%m-%d')

    today_start = datetime.datetime.strptime(today_str + '00:00:000000','%Y-%m-%d %H:%M:%S:%f')
    week_start = datetime.datetime.strptime(week_str + '00:00:000000','%Y-%m-%d %H:%M:%S:%f')
    month_start = datetime.datetime(year = today.year,month = today.month,day = 1 )

    today = statistics(today_start,shop,5)
    week = statistics(week_start,shop,5)
    month = statistics(month_start,shop,5)

    shop_is_new(shop)

    context = {
        'shop':shop,
        'today':today,
        'week':week,
        'month':month,
    }
    return render(request,'sj_index.html',context)


def statistics(day_start,shop,n):
    '''
    获取首页数据
    ：param  day_start:开始日期  日  周  月
    ：param  shop：店铺
    ：param  n：取消前n条数据
    ：return  <QuerySet> GoodsSku 与销售总额
    '''
    # 获取订单
    order_info = OrderInfo.objects.values_list('order_id').filter(create_time__gte=day_start,
                                                                  shop = shop,order_status__gt=5)

    # 获取订单明细
    order_goods = OrderGoods.objects.filter(order_id__in=order_info)

    # 根据订单构造字典，计算销售额（订单表存在商品总价字段，求和即可）
    id_count = {}
    total_price = 0
    for good_day in order_goods:
        total_price = total_price + good_day.price*good_day.count
        if good_day.sku_id in id_count.keys():
            id_count[good_day.sku_id] = int(id_count[good_day.sku_id]) + good_day.count
        else:
            id_count[good_day.sku_id] = good_day.count

    # 将构造的字典按value排序
    list_id_count = sorted(id_count.items(),key=lambda item:item[1],reverse=True)
    list_id_count_part = list_id_count[:n]
    orderly_data = {}
    for ls in list_id_count_part:
        orderly_data[ls[0]] = ls[1]

    # 拿出排序后字典的key，并查询出sku对象
    keys = list(orderly_data.keys())
    sku_info = GoodsSKU.objects.filter(id__in=keys)

    # 构造数据返回
    context = {'sku_info':sku_info,'total_price':total_price}

    return context



