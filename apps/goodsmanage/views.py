from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from apps.goods.models import Goods,GoodsSKU,GoodsType,GoodsImage
from apps.user.models import Shop
from django.views import View
from utils.fdfs.storage import FastDFSStorage
from utils.common import page_item,shop_is_new,goods_item


class SjcpglView(View):
    '''商家菜品管理页面'''

    def get(self,request,page):
        # 获取店铺信息
        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        # 获取店铺下所有商品
        goods_sku_info = GoodsSKU.objects.filter(shop_id = shop.id).order_by('-update_time')

        # 为商品添加图片
        goods_item(goods_sku_info)

        # 对数据进行分页
        context = page_item(goods_sku_info,page,10)
        shop_is_new(shop)
        context['shop'] = shop

        return render(request,'sj_cpgl.html')

    def post(self,request):
        '''处理商品上架'''

        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        pack = request.POST.get('pack')
        typ = request.POST.get('type')
        img = request.FILES.get('img')

        # 校验基本数据
        if not all([name,price,stock,pack,typ,img]):
            return render(request,'sj_cpgl.html',{'errmsg':'缺少相关数据'})

        # FDFS 上传图片
        rec = FastDFSStorage().save(img.name,img)

        # 业务表添加数据
        try:
            shop = Shop.objects.get(user_id = request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        goods = Goods(name = name,shop_id=shop.id)
        goods.save()

        # 确定是否为新增类型
        try:
            goods_type = GoodsType.objects.get(name = typ,shop_id = shop.id)
        except :
            goods_type = GoodsType(name = typ,shop_id = shop.id)
            goods_type.save()

        goods_sku = GoodsSKU(goods=goods,goods_type=goods_type,name=name,
                             price = price,unite = 'per',stock=stock,pack=pack)
        goods_sku.save()

        goods_image = GoodsImage(img = rec,sku_id=goods_sku.id)
        goods_image.save()

        return render(request,'sj_cpgl.html')


class SjcpglUpdateView(View):
    '''商品修改'''
    def get(self,request,goods_id):
        '''展示页面'''

        try:
            goods_sku = GoodsSKU.objects.get(id = goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goodsmanage:sj_cpgl'))

        # 获得商品图片
        goods_item(goods_sku)

        try:
            shop = Shop.objects.get(user_id = request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效，请重新登录'})

        return render(request,'sj_cpgl_update.html',{'sku':goods_sku,'shop':shop})

    def post(self,request,goods_id):
        '''提交商品修改'''
        # 接收数据
        sku_id = goods_id
        file = request.POST.get('file')
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        typ = request.POST.get('type')
        pack = request.POST.get('pack')

        # 校验基本数据
        if not all([file,name,price,stock,typ,pack]):
            return render(request,'sj_cpgl.html',{'errmsg':'缺少相关数据'})

        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return render(request,'login.html',{'errmsg':'用户登录信息已失效'})

        # 若修改的是商品类型，则需要验证商品类型是否已经存在
        try:
            goods_type = GoodsType.objects.get(name=typ,shop_id=shop.id)
        except GoodsType.DoesNotExist:
            goods_type = GoodsType(name=typ,shop_id=shop.id)
            goods_type.save()

        try:
            sku = GoodsSKU.objects.get(id = sku_id)
        except GoodsSKU.DoesNotExist:
            return render(request,'login.html',{'errmsg':'数据错误，请重新登录！'})

        # 暂未校验sku_id 与该用户是否存在所属关系

        sku.name = name
        sku.price = price
        sku.stock = stock
        sku.pack = pack
        sku.type = goods_type
        sku.save()

        # 是否对商品图片进行了修改
        if file:
            good_image = GoodsImage.objects.get(sku_id=sku.id)
            # FDFS 上传图片
            rec = FastDFSStorage().save(file.name,file)
            good_image.image = rec
            good_image.save()

        return redirect(reverse('goodsmanage:sj_cpgl',kwargs={'page':1}))

    def update_del(self,request,sku_id):
        '''处理商品删除'''
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return render(request,'login.html',{'errmsg':'数据错误，请重新登录'})

        type = sku.type
        sku.delete()

        # 该商家该类型下最后一件商品被删除时，该类型也删除
        goods_type = GoodsSKU.objects.get(goods_type=type).count()
        if goods_type == 0:
            type.delete()

        return redirect(reverse('goodsmanage:sj_cpgl',kwargs={'page':1}))



