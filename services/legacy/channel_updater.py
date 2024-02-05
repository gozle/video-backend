import os
import sys
import django

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()
from files.models import Channel
from urllib.error import HTTPError
from yt_dlp.utils import DownloadError
from assets.YoutubeScripts import YT
from assets.db_functions import create_playlist, create_video
import sys

# Get the list of arguments passed to the script
args = sys.argv


# Check if 'reverse' is in the arguments
# TODO: Refactor this function to make it more readable
# TODO: Is not downloading all videos of channel :( Fix this

def update_channel():
    yt = YT()
    while True:
        # If reverse in kwargs, get queryset reversed
        if 'reverse' in args:
            channels = Channel.objects.all().order_by('-pk')[3:]
        else:
            channels = Channel.objects.all()
            last_3_pks = list(channels.values_list('pk', flat=True))[-3:]
            channels = channels.exclude(pk__in=last_3_pks)

        for to_download in channels:
            channel_id = to_download.channel_id
            print('[CHANNEL FOUND]', channel_id)
            channel = yt.get_channel(channel_id)
            print('Getting playlists....')
            playlists = []
            try:
                playlists = yt.get_playlists_from_channel(channel['id'])
            except:
                pass
            print('Getting videos....')
            videos = yt.get_all_videos_from_channel(channel['id'])

            print('Creating playlists....')
            for playlist in playlists:
                try:
                    create_playlist(playlist)
                    videos = yt.get_videos_from_playlist(
                        playlist['id'], videos)
                except Exception as e:
                    print(e)
                    pass

            print('[NUMBER OF VIDEOS]', len(videos))
            print('Creating videos....')
            # videos.reverse()
            response = ''
            for video in videos:
                while True:
                    try:
                        response = create_video(
                            yt, video, channel['id'], to_download.all_video)
                        break
                    except DownloadError:
                        print('[DOWNLOAD ERROR]', video['channel_id'])
                        break
                    except HTTPError:
                        print("[HTTPERROR]", video['channel_id'])
                        break
                if response == 'passed':
                    break
                if response == 'reverse':
                    break
            if response == 'reverse':
                print('[REVERSED]')
                videos.reverse()
                for video in videos:
                    while True:
                        try:
                            response = create_video(
                                yt, video, channel['id'], to_download.all_video)
                            break
                        except DownloadError:
                            print('[DOWNLOAD ERROR]', video['channel_id'])
                            break
                        except HTTPError:
                            print("[HTTPERROR]", video['channel_id'])
                            break



update_channel()
