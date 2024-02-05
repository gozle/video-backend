import logging
from time import sleep

from django import db

from lib.rabbitmq import *
from lib.rabbitmq_consumer import ReconnectingConsumer
from lib.rabbitmq_queue import Queue
from lib.stoppable_thread import StoppableThread

from services.utils.tube import download_video
from services.utils.functions import download_image, get_from_local, get_dar
from files.models import Video


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def index_channel_callback(message, queue):
    video_id = message
    db.connections.close_all()
    print('[DOWNLOADING]', video_id)

    try:
        video = Video.objects.get(video_id=video_id)
        if video.video:
            raise Exception
    except Exception as e:
        print('ERROR FUXK', e)
        return

    path = settings.TEMP_PATH
    try:
        data = download_video(video_id, path)
        if not data:
            print('No data', video_id)
            return
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as e:
        print(e)
        return

    image = download_image(data["thumbnail_url"])
    db.connections.close_all()

    video.thumbnail.save(video.video_id + ".png", image)
    video.video.save(video.video_id + ".webm", get_from_local(data["path"]))
    video.server = settings.SERVER
    video.expansion = get_dar(data["path"])
    video.save()

    print("[COMPLETED]", video.title)
    return


def start_consumer(queue):
    consumer = ReconnectingConsumer(
        amqp_url,
        app_id,
        queue,
        exchange,
        exchange_type,
        prefetch_count=1
    )
    consumer.run()


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    queues = [
        Queue('videos-to-download', 'videos_download', consume_callback=index_channel_callback),
    ]

    db.connections.close_all()
    threads = []
    for queue in queues:
        threads.append(
            StoppableThread(
                target=start_consumer,
                args=(queue,)
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

