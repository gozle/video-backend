import pika
from urllib.parse import quote
from django.conf import settings
from pika.exchange_type import ExchangeType


host = settings.RABBITMQ.get('host')
port = settings.RABBITMQ.get('port')
user = settings.RABBITMQ.get('username')
password = settings.RABBITMQ.get('password')
vhost = settings.RABBITMQ.get('vhost')
vhost_safe = quote(vhost, safe='')

app_id = settings.RABBITMQ.get('app_id')
exchange = settings.RABBITMQ.get('exchange')
exchange_type = ExchangeType.direct

amqp_url = f'amqp://{user}:{password}@{host}:{port}/{vhost}'
properties = pika.BasicProperties(app_id=app_id, content_type='application/json')
