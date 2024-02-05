import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()
import sys
from assets.db_functions import create_playlist, create_video
from assets.YoutubeScripts import YT
from yt_dlp.utils import DownloadError
from urllib.error import HTTPError
from django.conf import settings
from files.models import Channel

# Get the list of arguments passed to the script
args = sys.argv

# Check if 'reverse' is in the arguments


def update_channel():
    yt = YT()
    while True:
        ids = [891, 890, 889]
        channels = Channel.objects.filter(id__in=ids)

        for to_download in channels:
            id = to_download.channel_id
            print('[CHANNEL FOUND]', id)
            channel = yt.get_channel(id)
            print('Getting playlists....')
            playlists = []
            try:
                playlists = yt.get_playlists_from_channel(channel['id'])
            except:
                pass
            print('Getting videos....')
            videos = yt.get_all_videos_from_channel(
                    channel['id'], get_all=True)

            print('Creating playlists....')
            for playlist in playlists:
                while True:
                    try:
                        create_playlist(playlist, settings.SERVER)
                        videos = yt.get_videos_from_playlist(
                            playlist['id'], videos)
                        break
                    except Exception as e:
                        print(e)
                        pass

            print('[NUMBER OF VIDEOS]', len(videos))
            print('Creating videos....')
            response = ''
            for video in videos:
                while True:
                    try:
                        response = create_video(
                            yt, video, channel['id'], settings.SERVER, settings.TEMP_PATH)
                        break
                    except DownloadError:
                        print('[DOWNLOAD ERROR]', video['id'])
                        break
                    except HTTPError:
                        print("[HTTPERROR]", video['id'])
                        break


update_channel()
