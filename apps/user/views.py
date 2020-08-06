import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from apps.user.models import User,Address,Shop,ShopTypeDetail
from utils import common
from itsdangerous import TimedJSONWebSignatureSerializer as TJSS, SignatureExpired
from celery_execute_task.sendmail import send_activate_email

# Create your views here.

class RegisterView(View):
    """注册"""
    def get(self,request):
        """显示注册页面"""

        # 买家注册页面
        return render(request,'register.html')

    def post(self,request):
        """显示注册处理"""

        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        receiver = request.POST.get('receiver')
        phone = request.POST.get('phone')
        addr = request.POST.get('addr')
        email = request.POST.get('email')
        sex = request.POST.get('sex')
        mjsj = request.POST.get('mjsj')
        img = request.FILES.get('file')

        # 校验数据
        if not all([username,password,cpassword,receiver,
                    phone,addr,email,sex,mjsj,img]):
            # 缺少相关数据
            return render(request,'register.html',{'errmsg':'缺少相关数据'})

        # 校验密码是否一致
        if not (password==cpassword):
            # 两次密码输入不一致
            return render(request,'register.html',{'errmsg':'两次输入密码不一致'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z0-9]{2,5}){1,2}$',email):
            # 邮箱不规范
            return render(request,'register.html',{'errmsg':'邮箱不规范'})

        # 校验用户名是否重复
        if common.verify_exist(request,'username',username):
            return render(request,'register.html',{'errmsg':'用户名已存在'})

        # 校验手机号码是否重复
        if common.verify_exist(request,'phone',phone):
            return render(request,'register.html',{'errmsg':'手机号码已存在'})

        # 校验邮箱是否重复
        if common.verify_exist(request,'email',email):
            return render(request,'register.html',{'errmsg':'邮箱已存在'})


        # 业务处理
        # 为user表添加数据
        user = User.objects.create_user(username,email,password)
        # 1 男 0 女
        user.sex = sex
        # 0 买家 1 卖家
        user.is_staff = mjsj
        user.phone = phone
        user.real_name = receiver

        # 以二进制的形式读取file文件
        file_content = ContentFile(img.read())
        user.image.save(img.name,file_content)
        user.is_active = 0

        user.save()

       #  print('发送验证邮件')
        # 处理发送邮件
        # 加密用户的身份信息，生成token
        serializer = TJSS(settings.SECRET_KEY,900)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        # print(type(token))
        # 默认解码为utf8
        token = token.decode()
        # 使用celery发送邮件
        send_activate_email.delay(email,username,token)

        # print('为address存储数据')
        # 为address 表添加数据
        address = Address()
        address.receiver = receiver
        address.phone = phone
        address.addr = addr
        address.is_default = True
        address.user = user
        lat_lng = common.get_lng_lat(addr)
        address.lng = lat_lng['lng']
        address.lat = lat_lng['lat']
        address.save()




        # 返回响应
        if int(mjsj):
            # 店铺注册页面
            return render(request,'sj_register.html',{'user':user.id})
        else:
            # 买家登录界面
            return redirect(reverse('user:login'))


class UserActivate(View):
    """用户通过邮件激活功能"""

    def get(self,request,token):
        """点击邮件链接激活业务处理"""
        serializer = TJSS(settings.SECRET_KEY,900)
        try:
            info = serializer.loads(token)

            # 获取要激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id = user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录界面
            return redirect(reverse('user.login'))

        except SignatureExpired as se:
            # 激活链接已过期
            return HttpResponse('激活链接已过期，请注意查收新的激活邮件')



class ShopRegister(View):
    ''''商家店铺注册处理'''
    def get(self,request):
        '''显示注册页面'''
        return render(request,'sj_register.html')

    def post(self,request):
        '''显示注册处理'''
        shop_name = request.POST.get('shop_name')
        shop_addr = request.POST.get('shop_addr')
        shop_type = request.POST.get('shop_style')
        shop_user = request.POST.get('shop_user')
        shop_price = request.POST.get('shop_price')
        img = request.POST.get('shop_file')
        receive_start = request.POST.get('receive_start')
        receive_end = request.POST.get('receive_end')
        if not all([shop_name,shop_addr,shop_price,shop_type,shop_user,
                   receive_end,receive_start,img]):
            # 数据不完整
            return render(request,'sj_register.html',{'errmsg':'店铺名已存在'})

        # 校验店铺名是否重复
        try:
            shop = Shop.objects.get(shop_name=shop_name)
        except  Shop.DoesNotExist:
            shop = True
        if shop:
            return render(request,'sj_register.html',{'errmsg':'店铺名已存在'})

        shop = Shop(
            shop_name = shop_name,
            shop_type = shop_type,
            shop_addr = shop_addr,
            user_id = shop_user,
            shop_price = shop_price,
            receive_start = receive_start,
            receive_end = receive_end,
            high_opinion = '0',
        )
        shop.save()
        return redirect(reverse('user:login'))


class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录页面'''

        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ""
            checked = ""

        # 使用模板
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        '''登录校验'''

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)

        # 校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'请输入用户名和密码'})

        print('密码验证')
        # 业务处理:登录校验
        user = None
        login_user = authenticate(username=username,password=password)
        print(login_user)
        login_phone = authenticate(phone = username,password=password)
        login_email = authenticate(email = username,password = password)

        if login_user is not None:
            user = login_user
        if login_phone is not None:
            user = login_phone
        if login_email is not None:
            user = login_email

        print(user)
        if user:
            print('用户激活验证')
            # 用户名和密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request,user)

                print('账号性质验证')
                #  判断商家还是买家，跳转不同页面，1为商家
                if user.is_staff:
                    response = redirect(reverse('goods:sj_index'))
                else:
                    response = redirect(reverse('goods:index'))
                return response
            else:
                # 用户未激活
                return redirect(request,'login.html',{'errmsg':'用户未激活'})
        else:
            # 用户名或密码错误
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})


class LogoutView(View):
    '''退出登录'''
    def get(self,request):
        '''退出登录'''

        # 清除session
        logout(request)
        return redirect(reverse('user:login'))


def find_type(request):
    '''根据店铺类型获取具体类型'''

    type_detail = request.GET.get('type_detail')
    shop_type_detail = serializers.serialize('json',
                    ShopTypeDetail.objects.filter(type_code__contains=type_detail))
    return HttpResponse(shop_type_detail)

