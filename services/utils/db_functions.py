from django import db
from django.conf import settings
from services.utils.functions import remove_emojis, download_image

from files.models import Channel, Playlist, Video


def is_exists_channel(channel_id):
    if Channel.objects.filter(channel_id=channel_id).exists():
        return True
    return False


def is_exists_playlist(playlist_id):
    if Playlist.objects.filter(playlist_id=playlist_id).exists():
        return True
    return False


def is_exists_video(video_id):
    if Video.objects.filter(video_id=video_id).exists():
        return True
    return False


def create_channel(metadata):
    channel = Channel.objects.create(
        channel_id=metadata.get('channel_id'),
        title=remove_emojis(metadata.get('title')),
        description=remove_emojis(metadata.get('description')),
        tags=remove_emojis(metadata.get('tags')),
        server=settings.SERVER
    )

    channel.save()

    channel.avatar.save(str(channel.channel_id) + ".png", download_image(metadata.get('avatar')))
    if metadata.get('thumbnail'):
        channel.thumbnail.save(str(channel.channel_id) + ".png", download_image(metadata.get('thumbnail')))


def create_playlist(metadata, channel_id):
    try:
        channel = Channel.objects.get(channel_id=channel_id)
    except Exception as e:
        print("Can not find channel")
        return False

    playlist = Playlist.objects.create(
        playlist_id=metadata.get('playlist_id'),
        title=remove_emojis(metadata.get('title')),
        server=settings.SERVER,
        channel=channel
    )

    playlist.save()

    playlist.thumbnail.save(str(playlist.playlist_id) + ".png", download_image(metadata.get('thumbnail')))


def create_video(metadata, channel_id):
    try:
        channel = Channel.objects.get(channel_id=channel_id)
    except Exception as e:
        print("Can not find channel")
        return False

    if is_exists_video(metadata.get('id')):
        print('Video already exists', metadata.get('id'))
        return

    video = Video.objects.create(
        video_id=metadata.get('id'),
        title=remove_emojis(metadata.get('title')),
        description=remove_emojis(metadata.get('description')),
        duration=metadata.get("duration"),
        published_at=metadata.get("published_at"),
        server=settings.SERVER,
        channel=channel
    )

    video.save()


