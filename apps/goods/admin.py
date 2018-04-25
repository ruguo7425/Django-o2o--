from django.contrib import admin

# Register your models here.
from apps.goods.models import GoodsSPU, GoodsCategory, GoodsSKU, GoodsImage, IndexSlideGoods, IndexCategoryGoods, \
    IndexPromotion

admin.site.register(GoodsSPU)

admin.site.register(GoodsCategory)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexSlideGoods)
admin.site.register(IndexCategoryGoods)
admin.site.register(IndexPromotion)