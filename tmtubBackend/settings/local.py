from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", 'localhost']

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
DOMAIN = 'http://localhost'

MEDIA_ROOT = BASE_DIR / 'media'
TEMP_PATH = BASE_DIR / 'media/temp'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://127.0.0.1:9200',
        'http_auth': ('', ''),
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
        'HOST': '127.0.0.1',
        'PORT': '6379',
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