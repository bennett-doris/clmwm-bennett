# Generated by Django 3.0.8 on 2020-07-24 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommentInage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='order_info', verbose_name='图片路径')),
            ],
            options={
                'verbose_name': '订单评论图片',
                'verbose_name_plural': '订单评论图片',
                'db_table': 'order_image',
            },
        ),
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('count', models.IntegerField(default=1, verbose_name='商品数目')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品价格')),
                ('comment', models.CharField(max_length=256, verbose_name='评论')),
            ],
            options={
                'verbose_name': '订单商品',
                'verbose_name_plural': '订单商品',
                'db_table': 'order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('order_id', models.IntegerField(max_length=128, primary_key=True, serialize=False, verbose_name='订单id')),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], default=3, verbose_name='支付方式')),
                ('total_count', models.IntegerField(default=1, verbose_name='商品数量')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品总价')),
                ('transit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单运费')),
                ('order_status', models.SmallIntegerField(choices=[(1, '订单待支付'), (2, '订单已支付'), (3, '商家已接单'), (4, '骑手取货中'), (5, '订单配送中'), (6, '订单已送达'), (7, '订单已评价')], default=1, verbose_name='订单状态')),
                ('trade_no', models.CharField(max_length=128, verbose_name='支付编号')),
                ('comment', models.CharField(default='此用户未填写评价!', max_length=256, verbose_name='评论')),
                ('invoice_head', models.CharField(max_length=256, verbose_name='发票抬头')),
                ('taxpayer_number', models.CharField(max_length=22, verbose_name='纳税人识别号')),
                ('remarks', models.CharField(max_length=256, verbose_name='订单备注')),
                ('score', models.SmallIntegerField(default=10, verbose_name='订单综合评分')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'db_table': 'order_info',
            },
        ),
        migrations.CreateModel(
            name='OrderTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('status', models.SmallIntegerField(choices=[(1, '订单待支付'), (2, '订单已支付'), (3, '商家已接单'), (4, '骑手取货中'), (5, '订单配送中'), (6, '订单已送达'), (7, '订单已评价')], verbose_name='订单状态')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.OrderInfo', verbose_name='订单')),
            ],
            options={
                'verbose_name': '订单轨迹',
                'verbose_name_plural': '订单轨迹',
                'db_table': 'order_track',
            },
        ),
    ]
