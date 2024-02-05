import os
import sys
import django
from django.core.exceptions import ObjectDoesNotExist

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()
import time
from files.models import ChannelToDownload
from django.db.models import Q
from assets.db_functions import create_channel, create_playlist, create_video
from assets.YoutubeScripts import YT
from yt_dlp.utils import DownloadError
from urllib.error import HTTPError
from django.conf import settings


# TODO: Learn using logs


def add_channel():
    """
    Function to parse YouTube channels.
    """
    yt = YT()
    while True:
        # Try to get "to download" object from a database
        try:
            to_download = ChannelToDownload.objects.filter(
                Q(server=settings.SERVER, is_processing=True) | Q(is_processing=False))[0]
        except ObjectDoesNotExist:
            print('[CHANNEL NOT FOUND]. Trying to find...')
            time.sleep(5)
            continue
        print('[CHANNEL FOUND]', to_download.link)
        # Set is_processing to True
        # It is important that this is done in a separate thread
        to_download.is_processing = True
        to_download.server = settings.SERVER
        to_download.save()

        # Get id from channel link
        channel_id = to_download.link.split('/')[-1:][0]
        print('Parsing channell info...')
        channel = yt.get_channel(channel_id)
        # print(channel)
        print('Creating channel...')
        create_channel(channel, to_download.categories)

        print('Parsing playlists...')
        playlists = []
        try:
            playlists = yt.get_playlists_from_channel(channel['id'])
        except:
            pass
        print('[GOT PLAYLISTS]', len(playlists))
        print('Getting videos...')
        # Get videos of all playlists
        videos = yt.get_all_videos_from_channel(channel['id'])

        print('Creating playlists...')
        # Create playlists
        for playlist in playlists:
            try:
                create_playlist(playlist)
                videos = yt.get_videos_from_playlist(playlist['id'], videos)
                break
            except Exception as e:
                print(e)
                pass

        print('[NUMBER OF VIDEOS]', len(videos))
        print('Creating videos...')
        response = None
        for video in videos:
            try:
                response = create_video(
                    yt, video, channel['id'], to_download.all_video)
            except DownloadError:
                print('[DOWNLOAD ERROR]', video['id'])
                pass
            except HTTPError:
                print("[HTTP-ERROR]", video['id'])
                pass

            if response == 'passed':
                break
            if response == 'reverse':
                break

        # Delete to_download an object after completed parse
        to_download.delete()

        # if response == 'reverse':
        #     print('[REVERSED]')
        #     videos.reverse()
        #     for video in videos:
        #         while True:
        #             try:
        #                 response = create_video(
        #                     yt, video, channel['id'], settings.SERVER, settings.TEMP_PATH, to_download.all_video)
        #                 break
        #             except DownloadError:
        #                 print('[DOWNLOAD ERROR]', video['id'])
        #                 break
        #             except HTTPError:
        #                 print("[HTTP-ERROR]", video['id'])
        #                 break
        #
        #         if response == 'passed':
        #             break


add_channel()
