from .base import *

DEBUG = False

ALLOWED_HOSTS = ["v.gozle.com.tm", 'localhost', '172.16.1.215']

RABBITMQ = {
    "host": "172.16.1.92",
    "port": 5672,
    "vhost": "gozle_video",
    "username": "gozle_video",
    "password": "az6C6DwkQfIiliX",
    "app_id": "video_parser",
    "exchange": "video_parser"
}
SERVER = 1
DOMAIN = 'https://v.gozle.com.tm'

MEDIA_ROOT = '/srv/dbs/video/'
TEMP_PATH = '/srv/dbs/temp/'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://172.16.1.224:9200',
        'http_auth': ('music', 'aufhians@89fsain'),
        'verify_certs': False,
        'use_ssl': True,
        'ssl_show_warn': False,
        'timeout': 3600
    },
}

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gozle_video',
        'USER': 'video',
        'PASSWORD': 'videoismystiCALthingright?817**2__',
        'HOST': '172.16.1.92',
        'PORT': '2000',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
