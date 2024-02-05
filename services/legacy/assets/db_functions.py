from django.conf import settings
import os
import sys
import django

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()

from urllib.request import urlopen
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from datetime import datetime
from files.models import Channel, Video, Playlist
from services.legacy.assets.functions.functions import remove_emojis, get_dar

server = settings.SERVER
temp_path = settings.TEMP_PATH


def create_channel(channel, categories):
    channel_object = Channel.objects.filter(channel_id=channel['id'])
    if channel_object.exists():
        return
    avatar_temp = NamedTemporaryFile()
    avatar_temp.write(urlopen(channel['avatar_url']).read())
    avatar_temp.flush()
    banner_temp = None
    if channel['banner_url']:
        banner_temp = NamedTemporaryFile()
        banner_temp.write(urlopen(channel['banner_url']).read())
        banner_temp.flush()

    channel_object = Channel()
    channel_object.channel_id = channel['id']
    channel_object.name = remove_emojis(channel['title'])
    channel_object.description = channel['description']
    channel_object.keywords = channel['keywords']
    channel_object.server = server
    channel_object.save()
    for item in categories.all():
        channel_object.categories.add(item)

    channel_object.avatar.save(channel['id'] + '.png', File(avatar_temp))
    if banner_temp:
        channel_object.banner.save(channel['id'] + '.png', File(banner_temp))
    channel_object.save()
    print('[CHANNEL CREATED]', channel_object.name)


def create_playlist(metadata):
    playlist_object = Playlist.objects.filter(playlist_id=metadata['id'])
    if playlist_object.exists():
        return

    thumbnail_temp = NamedTemporaryFile()
    thumbnail_temp.write(urlopen(metadata['thumbnail_url']).read())
    thumbnail_temp.flush()
    playlist = Playlist()
    playlist.playlist_id = metadata['id']
    playlist.title = remove_emojis(metadata['title'])
    channel = Channel.objects.filter(channel_id=metadata['channel'])[0]
    playlist.channel = channel
    playlist.thumbnail.save(metadata['id'] + '.png', File(thumbnail_temp))
    playlist.server = server
    playlist.save()
    print('[CREATED PLAYLIST]', playlist.title)


def create_video(yt, video, channel_id, all_video):
    video_object = Video.objects.filter(video_id=video['id'])
    if video_object.exists():
        return
    try:
        playlist = Playlist.objects.get(
            playlist_id=video['playlist']) if video['playlist'] else None
    except:
        playlist = None
    channel = Channel.objects.get(channel_id=channel_id)

    metadata = yt.download_video(video['id'], temp_path, all_video)

    if metadata == 'reverse':
        return 'reverse'
    if metadata == 'passed':
        return 'passed'

    if not metadata:
        return

    thumbnail_temp = NamedTemporaryFile()
    thumbnail_temp.write(urlopen(metadata['thumbnail_url']).read())
    thumbnail_temp.flush()

    video = Video()
    video.video_id = metadata['id']
    video.title = remove_emojis(metadata['title'])

    if metadata['duration'] < 61:
        video.type = 'shorts'
    video.description = remove_emojis(metadata['description'])
    video.duration = metadata['duration']
    video.expansion = get_dar(metadata['video'])
    video.published_at = datetime.strptime(metadata['published_at'], '%Y%m%d')

    video.playlist = playlist if playlist else video.playlist
    video.channel = channel

    video.server = server

    video.thumbnail.save(metadata['id'] + '.png', File(thumbnail_temp))
    video.save()
    if metadata.get('subtitle'):
        video.subtitle.save(metadata['id'] + '.srt',
                            File(open(metadata['subtitle'])))
        os.remove(metadata['subtitle'])
    video.video.save(metadata['id'] + '.webm',
                     File(open(metadata['video'], 'rb')))
    os.remove(metadata['video'])

    print('[CREATED VIDEO]', video.title)


print(Video.objects.all())
