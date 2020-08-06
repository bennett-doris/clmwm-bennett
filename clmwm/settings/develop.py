from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clmwm',
        'USER':'root',
        'PASSWORD':'123456',
        'HOST':'192.168.1.116',
        'PORT':8306,
    }
}


# django 的缓存配置
CACHES = {
    'default':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':'redis://192.168.1.116:8379/1',
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient',
            # 提升redis 的解析性能
            'PAESER_CLASS':'redis.connection.Hiredisparser',
        }
    }
}

# 配置HayStack
HAYSTACK_CONNECTIONS= {
    'default':{
        # 设置搜索引擎，文件是apps 下的goods的whoosh_cn_backend.py
        # 如果goods模块未在apps下，请自动替换或去掉apps
        'ENGINE':'apps.goods.whoosh_cn_backend.WhooshEngine',
        'PATH':os.path.join(BASE_DIR,'whoosh_index'),
        'INCLUDE_SPELLING':True,

    },
}

# 当数据库改变时，自动更新索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


# 百度地图AK，申请服务端
BAIDU_AK = 'GcR4BkCh07kZPKupaiuktUlfRan6dzF9'

# 配置邮箱
# 发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SMTP 服务地址，使用其他服务器需更换
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'bennett_doris@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'RRNXFSNFARDFSFYY'
# 收件人看到的发件人
EMAIL_FROM = 'c0c<bennett_doris@163.com>'


# 配置支付宝支付服务
# APPID
ALIPAY_APPID = '2021000118607415'   # 沙箱APPID，生产环境必须更改为应用APPID
# 网关
# ALIPAY_URL = ‘
ALIPAY_URL= 'https://openapi.alipaydev.com/gateway.do'      # 沙箱网关，生产环境必须改为正式
# 使用秘钥文件
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR,'apps/order/app_private_key.pem')
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR,'apps/order/alipay_public_key.pem')


INSTALLED_APPS += [
    'debug_toolbar',    # 性能排查插件
]
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ['127.0.0.1']
