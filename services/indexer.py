import logging
from time import sleep

from django import db

from lib.rabbitmq import *
from lib.rabbitmq_consumer import ReconnectingConsumer
from lib.rabbitmq_queue import Queue
from lib.stoppable_thread import StoppableThread

from services.utils.db_functions import is_exists_channel, create_channel, is_exists_playlist, create_playlist, \
    is_exists_video, create_video
from services.utils.tube import get_channel_metadata, get_playlists_of_channel, get_videos_of_channel, filter_videos


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def add_video(video, channel_id):
    create_video(video, channel_id)
    print("[CREATED VIDEO]", video["title"])


def index_channel_callback(message, queue):
    channel_url = message

    print("[CHANNEL GOT]", channel_url)

    try:
        channel = get_channel_metadata(channel_url)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception:
        return

    db.connections.close_all()

    if not is_exists_channel(channel["channel_id"]):
        create_channel(channel)
        print("[CREATED CHANNEL]", channel["channel_id"])

    playlists = get_playlists_of_channel(channel["channel_id"])
    for playlist in playlists:
        if not is_exists_playlist(playlist["playlist_id"]):
            create_playlist(playlist, channel["channel_id"])
            print("[CREATED PLAYLIST]")

    print("GETTING VIDEOS OF CHANNEL...")
    videos = get_videos_of_channel(channel["channel_id"])
    print("[GOT VIDEOS, FILTERING...]")

    valid_videos = filter_videos(videos)
    db.connections.close_all()
    for metadata in valid_videos:
        add_video(metadata, channel["channel_id"])

    print("[DONE] ", channel["title"])


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
        Queue('channels-to-index-by-view', 'channels_by_view',
              consume_callback=index_channel_callback),
        Queue('channels-to-index-by-id', 'channels_by_id',
              consume_callback=index_channel_callback),
        Queue('channels-to-index-by-id-reverse', 'channels_by_id_reverse',
              consume_callback=index_channel_callback),
    ]
    db.connections.close_all()
    threads = []
    for queue in queues:
        for i in range(10):
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
