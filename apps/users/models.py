from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.models import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


class User(BaseModel, AbstractUser):
    """用户信息模型类"""

    class Meta:
        db_table = 'df_user'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def generate_active_token(self):
        """生成加密数据"""
        # 参数1：密钥，不能公开，用于解密
        # 参数２：加密数据失效时间(1天)
        serializer = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY, 3600 * 24)
        # 要加密的数据此处传入了一个字典，其格式是可以自定义的
        # 只要包含核心数据 用户id 就可以了，self.id即当前用户对象的id
        token = serializer.dumps({'confirm': self.id})
        # 类型转换： bytes -> str
        return token.decode()


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"
        verbose_name = "地址"
        verbose_name_plural = verbose_name
