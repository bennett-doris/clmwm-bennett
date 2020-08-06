import os

from alipay import AliPay
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render,redirect,reverse
from django.views import View

from apps.user.models import Shop
from apps.order.models import OrderInfo,OrderTrack
from utils.common import order_detail,shop_is_new


# Create your views here.
class SjOrderView(View):
    '''商家订单管理'''

    def get(self,request,page):
        try:
            shop = Shop.objects.get(user_id = request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        order_exam = order_detail(2,page,shop)
        order_pass = order_detail(3,page,shop)
        order_conduct = order_detail(4,page,shop)
        order_delivery = order_detail(5,page,shop)
        order_finish = order_detail(7,page,shop)
        order_cancel = order_detail(0,page,shop)

        shop_is_new(shop)

        context = {
            'shop':shop,
            'order_exam':order_exam,
            'order_pass':order_pass,
            'order_conduct':order_conduct,
            'order_delivery':order_delivery,
            'order_finish':order_finish,
            'order_cancel':order_cancel
        }

        return render(request,'sj_order.html',context)


class  OrderReceive(View):
    '''商家接受订单'''
    def get(self,request,order_id,order_status):
        try:
            shop = Shop.objects.get(user_id = request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录！'})

        # 校验参数
        if not order_id:
            return redirect(reverse('ordermanage:sj_order',kwargs = {'page':1}))

        try:
            order = OrderInfo.objects.get(order_id = order_id,order_status = 2)
        except :
            return redirect(reverse('ordermanage:sj_order',kwargs={'page':1}))

        # 改变订单状态，轨迹表生成一条数据
        order.order_status = order_status
        order_track = OrderTrack.objects.create(order=order,status = order_status)
        order_track.save()

        return redirect(reverse('ordermanage:sj_order',kwargs={'page':1}))


class OrderRefuse(View):
    '''商家拒接订单'''
    def get(self,request,order_id):
        try:
            shop = Shop.objects.get(user_id = request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        # 校验数据
        if not order_id:
            return redirect(reverse('ordermanage:sj_order',kwargs={'page':1}))

        try:
            order = OrderInfo.objects.get(order_id = order_id,status = 2)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('ordermanage:sj_order',kwargs={'page':1}))

        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,    # 默认回调url
            app_private_key_string=os.path.join(settings.BASE_DIR,'apps/order/app_private_key.pem'),
            # 支付宝的公钥
            alipay_public_key_string=os.path.join(settings.BASE_DIR,'apps/order/alipay_public_key.pem'),
            sign_type='RSA2',
            debug=True
        )

        order_string = alipay.api_alipay_trade_refund(
            trade_no=order.trade_no,
            refund_amount=str(order.total_price+order.transit_price),
            notify_urll = None
        )

        code = order_string.get('code')

        if code == '10000' and order_string.get('msg') == 'Success':
            # 改变订单状态，轨迹表生成一条数据
            order.order_status = 0
            order_track = OrderInfo.objects.create(order=order,status = 0)
            order_track.save()
        else:
            sub_msg = order_string.get('sub_msg')
            return render(request,'sj_oder.html',{'errmsg':sub_msg})

        return redirect(reverse('ordermanage:sj_order',kwargs={'page':1}))


def status(request):
    '''店铺 营业、休息 提示'''
    try:
        shop = Shop.objects.get(user_id=request.user.id)
    except Shop.DoesNotExist:
        return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

    shop_status = request.GET.get('status')

    if shop_status == '1':
        shop.business_do = True
        shop.save()
        return JsonResponse({'res':1,'mes':'营业中'})
    else:
        shop.business_do = False
        shop.save()
        return JsonResponse({'res':0,'mes':'休息中'})


