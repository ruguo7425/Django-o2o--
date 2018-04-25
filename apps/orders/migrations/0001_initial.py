# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('count', models.IntegerField(verbose_name='购买数量', default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('comment', models.TextField(verbose_name='评价信息', default='')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('order_id', models.CharField(serialize=False, max_length=64, primary_key=True, verbose_name='订单号')),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品总金额')),
                ('trans_cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='运费')),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], verbose_name='支付方式', default=1)),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态', default=1)),
                ('trade_no', models.CharField(max_length=100, unique=True, blank=True, verbose_name='支付编号', default='', null=True)),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
    ]
