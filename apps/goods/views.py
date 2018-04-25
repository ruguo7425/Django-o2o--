from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods


class BaseCartView(View):
    def get_cart_count(self, request):
        """获取购物车中商品的数量"""
        cart_count = 0
        # 如果用户登录，就获取购物车数据
        if request.user.is_authenticated():
            # 获取 StrictRedis 对象
            strict_redis = get_redis_connection()  # type: StrictRedis
            # 获取用户id
            user_id = request.user.id
            key = 'cart_%s' % user_id
            # 从redis中获取购物车数据，返回字典
            cart_dict = strict_redis.hgetall(key)
            # 遍历购物车字典的值，累加购物车的值
            for c in cart_dict.values():
                cart_count += int(c)

        return cart_count


class IndexView(BaseCartView):
    # def get(self, request):
    #     """显示首页"""
    #     return render(request, 'index.html')
    def get(self, request):
        """显示首页"""

        # 查询商品类别数据
        categories = GoodsCategory.objects.all()

        # 查询商品轮播轮数据
        # index为表示显示先后顺序的一个字段，值小的会在前面
        slide_skus = IndexSlideGoods.objects.all().order_by('index')

        # 查询商品促销活动数据
        promotions = IndexPromotion.objects.all().order_by('index')

        # 查询类别商品数据
        for category in categories:
            # 查询某一类别下的文字类别商品
            text_skus = IndexCategoryGoods.objects.filter(
                category=category, display_type=0).order_by('index')
            # 查询某一类别下的图片类别商品
            img_skus = IndexCategoryGoods.objects.filter(
                category=category, display_type=1).order_by('index')

            # 动态地给类别新增实例属性
            category.text_skus = text_skus
            # 动态地给类别新增实例属性
            category.img_skus = img_skus

        # 查询购物车中的商品数量
        # cart_count = self.get_cart_count(request)
        # 定义模板数据
        context = {
            'categories': categories,
            'slide_skus': slide_skus,
            'promotions': promotions,
            # 'cart_count': cart_count,
        }
        return render(request, 'index.html', context)
