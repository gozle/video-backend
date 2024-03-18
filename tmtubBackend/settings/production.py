from .base import *

DEBUG = True

ALLOWED_HOSTS = ["video-api.gozle.org", 'localhost', '172.16.1.215']
CSRF_TRUSTED_ORIGINS = ['https://video-api.gozle.org']

RABBITMQ = {
    "host": "172.16.1.92",
    "port": 5672,
    "vhost": "gozle_video",
    "username": "gozle_video",
    "password": "az6C6DwkQfIiliX",
    "app_id": "video_parser",
    "exchange": "video_parser"
}
SERVER = 5
DOMAIN = 'https://video-api.gozle.org'

MEDIA_ROOT = '/data/projects/video.gozle/film/db'
TEMP_PATH = '/data/projects/video.gozle/film/db/temp/'

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
        'NAME': 'gozle_film',
        'USER': 'film',
        'PASSWORD': 'ofakspQFOPAKSaf241',
        'HOST': '172.16.1.92',
        'PORT': '2000',
    }
}
