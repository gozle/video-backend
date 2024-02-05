import json
from time import sleep
from threading import current_thread

from django import db
from django.db.models import Q

from lib.rabbitmq import *
from lib.rabbitmq_queue import Queue
from lib.stoppable_thread import StoppableThread

from files.models import Channel, Video


def get_channels_by_view():
    db.connections.close_all()
    objs = []
    for channel in Channel.objects.all().order_by("-view"):
        objs.append(channel.channel_id)
    return objs


def get_channels_by_id():
    db.connections.close_all()
    objs = []
    for channel in Channel.objects.all().order_by('id'):
        objs.append(channel.channel_id)
    return objs


def get_channels_by_id_reverse():
    db.connections.close_all()
    objs = []
    for channel in Channel.objects.all().order_by('-id'):
        objs.append(channel.channel_id)
    return objs


def get_videos_to_convert():
    db.connections.close_all()
    objs = []
    for video in Video.objects.exclude(video="").filter(Q(m3u8=None) | Q(m3u8="")):
        objs.append(video.video_id)
    return objs


def get_videos_to_download():
    db.connections.close_all()
    objs = []
    for video in Video.objects.filter(Q(m3u8=None, video="") | Q(m3u8="", video="")).order_by("-channel__view"):
        objs.append(video.video_id)
    return objs


def publish_to_queue(amqp_url,
                     exchange, exchange_type,
                     message_properties,
                     queue):
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange,
                             exchange_type=exchange_type)

    while True:
        queue_frame = channel.queue_declare(queue=queue.name, durable=queue.durable)
        channel.queue_bind(queue.name,
                           exchange,
                           routing_key=queue.routing_key)
        if current_thread().stopped():
            connection.close()
            return
        if queue_frame.method.message_count == 0:
            for item in queue.publish_items:
                channel.basic_publish(exchange, queue.routing_key,
                                      json.dumps(item),
                                      message_properties)
        sleep(3)


def main():
    queues = [
        Queue('channels-to-index-by-view', 'channels_by_view',
              get_publish_items=get_channels_by_view),
        Queue('channels-to-index-by-id', 'channels_by_id',
              get_publish_items=get_channels_by_id),
        Queue('channels-to-index-by-id-reverse', 'channels_by_id_reverse',
              get_publish_items=get_channels_by_id_reverse),
        Queue('videos-to-download', 'videos_download',
              get_publish_items=get_videos_to_download),
    ]
    db.connections.close_all()
    threads = []
    for queue in queues:
        threads.append(
            StoppableThread(
                target=publish_to_queue,
                args=(amqp_url, exchange, exchange_type, properties, queue)
            )
        )
    for thread in threads:
        thread.start()

    try:
        while True:
            sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print('Received keyboard interrupt, quitting threads.')
        for thread in threads:
            thread.stop()


if __name__ == '__main__':
    main()
