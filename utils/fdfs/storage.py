# utils/fdfs/storage.py
from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    """自定义文件存储"""

    # 目前此方法相当于没有重写，因为还没有添加任何额外的逻辑
    def _save(self, name, content):
        """
        当用户通过管理后台上传文件时,
        django会调用此方法来保存用户上传到django网站的文件,
        我们可以在此方法中保存用户上传的文件到FastDFS服务器中
        """
        # content: ImageFieldFile对象, 可以从此对象读取文件内容
        # path = super()._save(name, content)
        # print('name=%s, content=%s, path= %s' % (name, type(content), path))
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            # 上传文件到FDFS服务器
            datas = content.read()  # 要上传的内容
            # 字典
            result = client.upload_by_buffer(datas)
            status = result.get('Status')
            if status == 'Upload successed.':
                path = result.get('Remote file_id')
            else:
                raise Exception('上传图片失败:%s' % status)
        except Exception as e:
            print(e)
            raise e

        # 返回文件id, django会自动保存此路径到数据库中
        return path

    def url(self, name):
        """返回图片显示时的url地址"""

        # 此url的值为: 数据库中保存的url路径的值
        url = super().url(name)
        # print(url)
        return 'http://127.0.0.1:8888/' + url