import re
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired
from redis import StrictRedis
from apps.goods.models import GoodsSKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import User, Address
from dailyfresh import settings
from utils.LoginRequiredMixin import LoginRequiredMixin
from celery_tasks.tasks import send_active_mail


class RegisterView(View):
    """注册视图"""

    def get(self, request):
        """进入注册界面 """
        return render(request, 'register.html')

    def post(self, request):
        """实现注册功能 """

        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 用户协议， 勾选后得到：on

        # todo: 校验参数合法性
        # 判断参数不能为空
        if not all([username, password, password2, email]):
            # return redirect('/users/register')
            return render(request, 'register.html', {'errmsg': '参数不能为空'})

        # 判断两次输入的密码一致
        if password != password2:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致'})

        # 判断邮箱合法
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        # 判断是否勾选用户协议(勾选后得到：on)
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选用户协议'})

        # 处理业务： 保存用户到数据库表中
        # django提供的方法，会对密码进行加密
        user = None
        try:
            user = User.objects.create_user(username, email, password)  # type: User
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:
            # 判断用户是否存在
            return render(request, 'register.html', {'errmsg': '用户已存在'})

        # todo: 发送激活邮件
        token = user.generate_active_token()
        # 方式1：同步发送：如果网络卡的话会延迟,会阻塞
        # RegisterView.send_active_mail(username, email, token)
        # sleep(5)
        # 方式2：使用celery异步发送：不会阻塞
        # 会保存方法名参数等到Redis数据库中
        send_active_mail.delay(username, email, token)

        # 响应请求
        return render(request, 'login.html')

        # @staticmethod
        # def send_active_mail(username, email, token):
        #     """发送激活邮件"""
        #     subject = '天天生鲜激活邮件'  # 标题，必须指定
        #     message = ''  # 正文
        #     from_email = settings.EMAIL_FROM  # 发件人
        #     recipient_list = [email]  # 收件人
        #     # 正文 （带有html样式）
        #     html_message = ('<h3>尊敬的%s：感谢注册天天生鲜</h3>'
        #                     '请点击以下链接激活您的帐号:<br/>'
        #                     '<a href="http://127.0.0.1:8000/users/active/%s">'
        #                     'http://127.0.0.1:8000/users/active/%s</a>'
        #                     ) % (username, token, token)
        #
        #     send_mail(subject, message, from_email, recipient_list,
        #               html_message=html_message)


class ActiveView(View):
    def get(self, request, token: str):
        """
        用户激活
        :param request:
        :param token: 对字典 {'confirm':用户id} 进行加密后得到的字符串
        :return:
        """
        try:
            # 解密token
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
            # 字符串 -> bytes
            # dict_data = s.loads(token.encode())
            dict_data = s.loads(token)
        except SignatureExpired:
            # 判断是否失效
            return HttpResponse('激活链接已经失效')

        # 获取用户id
        user_id = dict_data.get('confirm')
        # 修改字段为已激活
        User.objects.filter(id=user_id).update(is_active=True)
        # 响应请求
        return HttpResponse('激活成功,请登录')


class LoginView(View):
    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """处理登录操作"""

        # 获取登录参数
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 校验参数合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '请求参数不完整'})

        # 通过 django 提供的authenticate方法，
        # 验证用户名和密码是否正确
        user = authenticate(username=username, password=password)

        # 用户名或密码不正确
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})

        if not user.is_active:  # 注册账号未激活
            # 用户未激活
            return render(request, 'login.html', {'errmsg': '请先激活账号'})

        # 通过django的login方法，保存登录用户状态（使用session）
        login(request, user)
        # 获取是否勾选'记住用户名'
        remember = request.POST.get('remember')
        # 判断是否是否勾选'记住用户名'
        if remember != 'on':
            # 没有勾选，设置session数据有效期为关闭浏览器后失效
            request.session.set_expiry(0)
        else:
            # 已勾选，设置session数据有效期为两周
            request.session.set_expiry(None)
        # 登录成功后,要跳转到NEXT指向的界面
        next = request.GET.get('next')
        if next:
            # 不为空,则跳转到next指向的界面
            return redirect(next)
        else:
            # 响应请求，返回html界面 (进入首页)
            return redirect(reverse('goods:index'))


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """处理退出登录逻辑"""

        # 由Django用户认证系统完成：会清理cookie
        # 和session,request参数中有user对象
        logout(request)

        # 退出后跳转：由产品经理设计
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequiredMixin, View):
    """用户中心:个人信息界面"""

    def get(self, request):
        # todo: 从Redis中读取当前登录用户浏览过的商品
        strict_redis = get_redis_connection('default')  # type: StrictRedis
        # 读取所有的商品ID,返回一个列表
        key = 'history_%s' % request.user.id
        # 最多只取5个商品ID[3,1,2]
        sku_ids = strict_redis.lrange(key, 0, 4)
        # 根据商品ID,查询出商品对象

        # skus = GoodsSKU.objects.filter(id__in=sku_ids)
        skus = []
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            skus.append(sku)

        # 获取用户对象
        user = request.user

        # 查询用户最新添加的地址
        try:
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        # 定义模板数据
        data = {
            # 不需要主动传，django会传
            # 'user': user,
            'which_page': 1,
            'address': address,
            'skus': skus
        }

        # 响应请求,返回html界面
        return render(request, 'user_center_info.html', data)


class UserOrderView(LoginRequiredMixin, View):
    """
    用户订单页
    """

    def get(self, request, page_num):
        """显示订单列表界面"""

        # 查询当前用户所有订单
        orders = OrderInfo.objects.filter(
            user=request.user).order_by('-create_time')

        for order in orders:
            # 查询某一订单下所有的订单商品
            order_skus = OrderGoods.objects.filter(order=order)
            for order_sku in order_skus:
                # 计算商品的小计金额
                amount = order_sku.price * order_sku.count
                # 动态地给订单商品添加小计金额
                order_sku.amount = amount

            # 新增实例属性: 订单商品
            order.order_skus = order_skus
            # 新增实例属性: 实付金额
            order.total_pay = order.total_amount + order.trans_cost
            # 新增实例属性: 订单状态名称
            order.status_desc = OrderInfo.ORDER_STATUS.get(order.status)

        # 参数1: 所有分页数据
        # 参数2: 每页显示多少条
        paginator = Paginator(orders, 2)
        try:
            # 获取某一页数据
            page = paginator.page(page_num)
        except EmptyPage:
            page = paginator.page(1)

        # 定义模板显示的数据
        context = {
            'page': page,
            'which_page': 2,
            'page_range': paginator.page_range,
        }

        # 响应请求, 返回html界面
        return render(request, 'user_center_order.html', context)


class UserAddressView(LoginRequiredMixin, View):
    """用户中心--地址界面"""

    def get(self, request):
        """显示用户地址"""
        user = request.user
        try:
            # 查询用户地址：根据创建时间排序，最近的时间在最前，取第1个地址
            # 方式1：  可能会IndexError
            address = Address.objects.filter(user=request.user) \
                .order_by('-create_time')[0]
            # 方式2： 可能会报IndexError
            # address = request.user.address_set.order_by('-create_time')[0]
            # 方式3： 可能会报DoesNotExist错误
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        data = {
            # 不需要主动传, django会自动传
            # 'user':user,
            'address': address,
            'which_page': 3
        }
        return render(request, 'user_center_site.html', data)

    def post(self, request):
        """"新增一个地址"""

        # 获取用户请求参数
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')
        # 登录后django用户认证模块默认
        # 会保存user对象到request中
        user = request.user  # 当前登录用户

        # 校验参数合法性
        if not all([receiver, address, zip_code, mobile]):
            return render(request, 'user_center_site.html', {'errmsg': '参数不完整'})

        # 保存地址到数据库中
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=address,
            zip_code=zip_code,
            user=user
        )

        # 响应请求，刷新当前界面(/users/address)
        return redirect(reverse('users:address'))
