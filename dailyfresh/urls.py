from django.conf.urls import include, url
from django.contrib import admin
import tinymce.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^users/', include('apps.users.urls', namespace='users')),  # 用户模块
    url(r'^cart/', include('apps.cart.urls', namespace='cart')),  # 购物车模块
    url(r'^orders/', include('apps.orders.urls', namespace='orders')),  # 订单模块
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^accounts/', include('apps.users.urls')),
    url(r'^', include('apps.goods.urls', namespace='goods')),  # 商品模块
    url(r'^search/', include('haystack.urls')),


]
