from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods, GoodsSKU


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
    def get(self, request):
        """显示首页"""
        # 读取缓存:  键=值
        # index_page_data=context字典数据
        context = cache.get('index_page_data')
        if not context:  # 数据为空
            print('缓存为空,从Mysql数据库读取')
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
            context = {
                'categories': categories,
                'slide_skus': slide_skus,
                'promotions': promotions,
            }
            cache.set('index_page_data', context, 60 * 30)
        else:
            print('使用缓存')
        # 查询购物车中的商品数量

        cart_count = self.get_cart_count(request)
        # 定义模板数据

        context.update({'cart_count': cart_count})

        # template = loader.get_template('index.html')
        return render(request, 'index.html', context)


class DetailView(BaseCartView):
    def get(self, request, sku_id):

        # 查询商品详情信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 查询不到商品则跳转到首页
            # return HttpResponse('商品不存在')
            return redirect(reverse('goods:index'))

        # 获取所有的类别数据
        categories = GoodsCategory.objects.all()

        # 获取最新推荐
        new_skus = GoodsSKU.objects.filter(
            category=sku.category).order_by('-create_time')[0:2]

        # 查询其它规格的商品
        other_skus = sku.spu.goodssku_set.exclude(id=sku.id)

        # 获取购物车中的商品数量
        cart_count = self.get_cart_count(request)
        # 如果是登录的用户
        if request.user.is_authenticated():
            # 获取用户id
            user_id = request.user.id
            # 从redis中获取购物车信息
            redis_conn = get_redis_connection("default")
            # 保存用户的历史浏览记录
            # history_用户id: [3, 1, 2]
            # 移除现有的商品浏览记录
            key = 'history_%s' % request.user.id
            redis_conn.lrem(key, 0, sku.id)
            # 从左侧添加新的商品浏览记录
            redis_conn.lpush(key, sku.id)
            # 控制历史浏览记录最多只保存5项(包含头尾)
            redis_conn.ltrim(key, 0, 4)

        # 定义模板数据
        context = {
            'categories': categories,
            'sku': sku,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'other_skus': other_skus,
        }

        # 响应请求,返回html界面
        return render(request, 'detail.html', context)
