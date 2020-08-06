from django.db import models
from db.base_model import BaseModel
from apps import  user
# Create your models here.


class GoodsType(BaseModel):
    """商品类型模型"""
    name = models.CharField(max_length=20,verbose_name='种类名称')
    shop = models.ForeignKey('user.Shop',on_delete=models.CASCADE,
                             verbose_name='所属店铺')
    class Meta:
        db_table = 'goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name


class GoodsSKU(BaseModel):
    """商品SKU模型"""
    status_choices = (
        (0,'上线'),
        (1,'下线')
    )
    type = models.ForeignKey('GoodsSKU',on_delete=models.CASCADE,
                             verbose_name='商品种类')
    goods= models.ForeignKey('Goods',on_delete=models.CASCADE,
                             verbose_name='商品SPU')
    name = models.CharField(max_length=20,verbose_name='商品名称')
    desc = models.CharField(max_length=256,verbose_name='商品简介')
    price = models.DecimalField(max_digits=10,decimal_places=2,
                                verbose_name='商品价格')
    unite = models.CharField(max_length=20,verbose_name='商品单位')
    image = models.ImageField(upload_to='goods',verbose_name='商品图片')
    stock = models.IntegerField(default=1,verbose_name='商品库存')
    sales = models.IntegerField(default=0,verbose_name='商品销量')
    status = models.SmallIntegerField(choices=status_choices,default=1,
                                      verbose_name='商品状态')
    pack = models.CharField(max_length=20,verbose_name='包装费')

    class Meta:
        db_table = 'goods_sku'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class Goods(BaseModel):
    """商品SPU模型类"""
    shop = models.ForeignKey('user.Shop',on_delete=models.CASCADE,
                             verbose_name='所属店铺')
    name = models.CharField(max_length=20,verbose_name='商品SPU名称')
    detail = models.CharField(max_length=200,verbose_name='商品详情')

    class Meta:
        db_table = 'goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class GoodsImage(BaseModel):
    """商品SPU模型类"""
    sku = models.ForeignKey('GoodsSKU',on_delete=models.CASCADE,
                            verbose_name='商品')
    image = models.ImageField(upload_to='goods',verbose_name='图片路径')

    class Meta:
        db_table = 'goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
