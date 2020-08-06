import os
from datetime import datetime

from alipay import AliPay
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect,reverse
from django.views import View
from django.db import transaction

from apps.user.models import User,Shop
from apps.goods.models import Goods,GoodsSKU
from apps.order.models import OrderInfo,OrderGoods,OrderTrack
from django.conf import settings
from utils.common import calculate_distance_duration, page_item


# Create your views here.
class OrderGenerateView(View):
    '''处理订单生成'''
    def get(self,request):
        pass

    @transaction.atomic             # 保证该函数中所有数据库操作都在同一个事务中
    def post(self,request):

        # 验证是否登录
        try:
            user = User.objects.get(id = request.user.id)
        except User.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录！'})

        # 接收数据
        sku_str = request.POST.get('sku.id')[1:]
        addr = request.POST.get('address')
        remarks = request.POST.get('remarks')
        invoice_head = request.POST.get('invoice_head')
        taxpayer_number = request.POST.get('taxpayer_number')

        # 数据提取
        try:
            sku_ids = sku_str[4:sku_str.find('cm2=')-1].split('%2C')
            sku_counts =sku_str[sku_str.find('cm2=')+4:].split('%2C')
            sku_info = GoodsSKU.objects.get(id__in = sku_ids)
            for index,sku in enumerate(sku_info):
                goods = Goods.objects.get(id = sku.goods_id)
                shop = Shop.objects.get(id = sku.shop_id)
        except Exception:
            return redirect(reverse('user:login'),{'errmsg':'数据错误'})

        # 校验基本数据
        if not all([sku_str, shop , goods , sku_counts,sku_info]):
            # 数据不完整
            return render(request,'sj_cpgl.html',{'errmsg':'缺少相关数据'})

        # 订单id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)

        total_price,total_count,range_flag = 0,0,0

        # 设置事务保存点
        save_id = transaction.savepoint()
        try:
            # 重新计算运费
            distance = calculate_distance_duration(shop,user)

            # 订单表添加数据
            order = OrderInfo.objects.create(
                order_id = order_id,
                user_id=request.user.id,
                addr_id=addr,
                shop = shop,
                remarks=remarks,
                invoice_head=invoice_head,
                total_price=0,
                total_count=0,
                taxpayer_number=taxpayer_number,
                transit_price=distance
            )
            # 订单轨迹表添加一条数据
            order_track = OrderTrack.objects.create(order = order,status = 1)

            # 乐观锁尝试三次
            for i in range(3):
                if range_flag:
                    break

                # 生成订单明细
                for index,item in enumerate(sku_info):
                    # 判断商品库存
                    if int(item.stock) < int(sku_counts[index]):
                        return HttpResponse('商品库存不足')

                    # 插入数据
                    order_goods = OrderGoods.objects.create(
                        order = order,
                        sku = item,
                        price = item.price,
                        count = sku_counts[index],

                    )
                    # 更新库存，返回受影响的行数
                    stock = item.stock - int(sku_counts[index])
                    res = GoodsSKU.objects.filter(id = item.id,stock = item.stock).\
                        update(stock = stock,sales = item.sales+int(sku_counts[index]))

                    if res == 0:
                        if i == 2:
                            # 尝试的第三次
                            transaction.savepoint_rollback(save_id)
                            return HttpResponse('下单失败')
                        continue

                    # 累加计算订单信息表中的商品的总数量和总价格
                    order.total_count = total_count
                    order.total_price = total_price
                    order.save()

        except Exception as e:
            transaction.savepoint_rollback(save_id)

        # 提交事务
        transaction.savepoint_commit(save_id)
        total_all = int(order.transit_price)+total_price
        return render(request,'wm_pay.html',{'order':order,'shop':shop,'total_all':total_all})


class OrderPayView(View):
    '''订单支付'''

    def post(self,request):
        '''
        调用封装好的接口
        python-alipay-sdk
        订单支付
       '''

        # 用户是否登录
        user = request.user
        if not user .is_authenticated:
            return JsonResponse({'res':0,'errmsg':'用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res':1,'errmsg':'无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id = order_id,user = user,order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res':2,'errmsg':'订单错误'})

        # 校验店铺是否营业
        if not order.shop.business_do:
            return JsonResponse({'res':4,'errmsg':'店铺已休息'})

        # 业务处理，使用python_sdk 调用支付接口
        # 初始化
        alipay = AliPay(
            appid = settings.ALIPAY_APPID,  # 应用id
            app_notify_url=None,        # 默认回调url
            app_private_key_string=os.path.join(settings.BASE_DIR,'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
            alipay_public_key_string=os.path.join(settings.BASE_DIR,'apps/order/alipay_public_key.pem'),
            sign_type = 'RSA2',     # RSA或RSA2
            debug = True,   # 默认为False
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到 https://openapi.alipaydev.com/gateway.do?+order_string
        # total_pay = order.total_price + order.transit_price
        total_amount = int(order.total_price+order.transit_price)
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,      # 订单id
            total_amount=str(total_amount),      # 支付总金额
            subject='吃了么外卖%s' %order_id,
            return_url=None,
            notify_url=None     # 可选，不填则使用默认notify url
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?'+order_string
        return JsonResponse({'res':3,'pay_url':pay_url})


class CheckPayView(View):
    '''查看支付订单的结果'''

    def post(self,request):
        '''查询支付结果'''

        # 用户是否登录
        user = request.user
        if user.is_authenticated:
            return JsonResponse({'res':0,'errmsg':'用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res':1,'errmsg':'无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,user=user,order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res':2,'errmsg':'订单错误'})

        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
            alipay_public_key_string=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type='RSA2',  # RSA或RSA2
            debug=True,  # 默认为False
        )

        # 调用支付宝的交易查询接口
        while True:
            # 网络不好会导致接口调用失败
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get('code')

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功，获取支付宝交易号
                trade_no = response.get('trade_no')

                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 2      # 待评价
                order.save()

                # 订单轨迹表生成新数据
                order_track = OrderTrack.objects.create(order=order,status = 2)

                # 返回结果
                return JsonResponse({'res':3,'message':'支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # 业务处理失败，可能一会儿会成功
                import  time
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res':4,'errmsg':'支付失败'})


class OrderBuySuccessView(View):
    '''支付成功，跳转详情页面'''
    def get(self,request,order_id,is_comment = False):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0,'errmsg':'用户未登录'})

        try:
            order_info = OrderInfo.objects.get(order_id = order_id,user = user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res':1,'errmsg':'订单错误'})

        order_goods = OrderGoods.objects.get(order = order_info)
        pay_price = int(order_info.total_price)+int(order_info.transit_price)
        order_track = OrderTrack.objects.filter(order = order_info,user = user,status__gt=1)

        # 预计送达时间
        arrive_time = order_info.create_time + datetime.timedelta(minutes = order_info.transit_price)

        context = {'order':order_info,'order_goods':order_goods,
                   'pay_price':pay_price,'order_track':order_track,
                   'arrove_time':arrive_time}

        # 控制页面跳转
        if is_comment:
            return context
        else:
            return render(request,'wm_ordertrack.html',context)

    def post(self):
        pass


class QueryOrderVIew(View):
    '''订单查询'''
    def get(self,request,page):
        '''查询订单'''
        
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0,'errmsg':'用户未登录'})
        
        # 进行中的订单
        order_going = OrderInfo.objects.filter(user = user,order_status_gte = 2,order_status_lt = 6)
        # 进行中的订单的商品明细
        order_going_goods = OrderGoods.objects.filter(order__in = order_going)
        # 已完成的订单
        order_finish = OrderInfo.objects.filter(user = user,order_status_gte=7)
        # 已完成的订单的商品明细
        order_finish_goods = OrderGoods.objects.filter(order__in=order_finish)
        # 分页处理
        order_going = page_item(order_going,page,10)
        order_finish = page_item(order_finish,page,10)
        order_going.update({'order_going_goods':order_going_goods})
        order_finish.update({'order_finish_goods':order_finish_goods})
        return render(self.request,'wm_query_order.html',{'order_going':order_going,'order_finish':order_finish})
        

class GoCommentView(View):
    def get(self,request,order_id):
        '''跳转到评论页面'''
        context = OrderBuySuccessView.get(self,request,order_id,is_comment = True)
        return render(request,'wm_buysuccess.html',context)
    