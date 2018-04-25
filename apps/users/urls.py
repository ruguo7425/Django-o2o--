from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # 处理登录操作
    # url(r'^do_register$', views.do_register, name='do_register'),
    url(r'^register$', views.RegisterView.as_view(), name='register'),  # 注册
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'),  # 激活
    url(r'^login/$', views.LoginView.as_view(), name='login'),  # 登录
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),  # 退出

    url(r'^address$', views.UserAddressView.as_view(), name='address'),  # 用户中心:地址
    url(r'^orders$', views.UserOrderView.as_view(), name='orders'),  # 用户中心:订单
    url(r'^info$', views.UserInfoView.as_view(), name='info'),  # 用户中心:个人信息

]
