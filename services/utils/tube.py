import datetime
import os

from django import db
from yt_dlp import YoutubeDL
from services.utils.functions import find_object_by_id, get_best_video, get_best_audio
from services.utils.db_functions import is_exists_video
from youtubesearchpython import *


def get_channel_metadata(channel_url):
    if not channel_url.startswith('https://youtube.com'):
        channel_url = "https://youtube.com/channel/" + channel_url

    ydl_opts = {
        'dumpjson': True,
        # 'flat_playlist': True,
        'extract_flat': True,
        'skip_download': True,
        "quiet": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        metadata = ydl.extract_info(channel_url, download=False)

        channel_data = {
            "id": metadata["id"],  # The id of the channel, example "@evrimagaci"
            "title": metadata["title"],  # The title of the channel, example "Evrim Ağacı"
            "channel_id": metadata["channel_id"],  # The YouTube id of the channel, example "UCatnasFAiXUvWwH8NlSdd3A"
            "description": metadata["description"],  # The description of the channel, example "description of channel"
            "tags": metadata["tags"],  # The tags of the channel, example "['bilim', 'evrim', '"evrim', 'agaci"']"
            "avatar": find_object_by_id(metadata["thumbnails"], "avatar_uncropped", default={"url": None})["url"],
            # The thumbnail url or None
            "thumbnail": find_object_by_id(metadata["thumbnails"], "banner_uncropped", default={"url": None})["url"],
            # The thumbnail url or None
        }

    return channel_data


def get_playlists_of_channel(channel_url):
    print(channel_url)
    channel = Channel(channel_url)
    while channel.has_more_playlists():
        channel.next()

    playlists = []

    for playlist in channel.result["playlists"]:
        metadata = dict()
        metadata["playlist_id"] = playlist["id"]
        metadata["thumbnail"] = playlist["thumbnails"][0]["url"]
        metadata["title"] = playlist["title"]
        playlists.append(metadata)

    return playlists


def get_videos_of_channel(channel_url):
    playlist = Playlist(playlist_from_channel_id(channel_url))

    print(f'Videos Retrieved: {len(playlist.videos)}')

    while playlist.hasMoreVideos:
        print('Getting more videos...')
        playlist.getNextVideos()
        print(f'Videos Retrieved: {len(playlist.videos)}')

    return playlist.videos


def filter_videos(videos, add_video, channel_id):
    for video in videos:
        try:
            try:
                if is_exists_video(video["id"]):
                    continue
            except:
                db.connections.close_all()
                if is_exists_video(video["id"]):
                    continue
            link = "https://youtube.com/watch?v=" + video["id"]
            ydl_opts = {"quiet": True}
            with YoutubeDL(ydl_opts) as (ydl):
                # Extract information about the video
                try:
                    info_dict = ydl.extract_info(link, download=False)
                except:
                    continue
                metadata = dict()
                metadata['id'] = info_dict['id']
                metadata['title'] = info_dict['fulltitle']
                metadata['description'] = info_dict['description']
                metadata['duration'] = info_dict['duration']
                metadata['thumbnail_url'] = info_dict['thumbnail']
                metadata['published_at'] = datetime.datetime.strptime(info_dict['upload_date'], '%Y%m%d')
                if metadata['duration'] and metadata['duration'] > 7200:
                    print('[DURATION IS TOO LARGE]')
                    continue
                if metadata['published_at'] > datetime.datetime.now() - datetime.timedelta(days=365):
                    print(metadata['id'], metadata['title'], metadata['duration'] // 60, 'minutes')
                    try:
                        add_video(metadata, channel_id)
                    except:
                        db.connections.close_all()
                        add_video(metadata, channel_id)
                # else:
                #     print("[INVALID]", metadata["title"])
        except Exception as e:

            print("[ERROR]", e)
            continue


def format_selector(ctx):
    """
    Function for selecting the best video and audio formats.
    Args:
        ctx: The context of the command.

    Returns:
        The best video and audio formats.
    """
    formats = ctx.get('formats')[::-1]
    # Get the best video format
    best_video = get_best_video(formats)
    if not best_video:
        print('[VIDEO IS NOT FOUND]')
        return None

    # Select the best audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # Get the best audio format
    best_audio = get_best_audio(formats, audio_ext)
    if not best_audio:
        print('[AUDIO OF VIDEO IS NOT FOUND]')
        return None

    # Yield the best video and audio formats
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


def download_video(video_id, path):
    link = "https://youtube.com/watch?v=" + video_id
    ydl_opts = {"quiet": True,
                "format": format_selector,  # This will select the specific resolution typed here
                "outtmpl": os.path.join(path, video_id), }
    with YoutubeDL(ydl_opts) as (ydl):
        # ExtracSt information about the video
        ydl.download(link)
        info_dict = ydl.extract_info(link, download=False)
        if os.path.isfile(os.path.join(path, video_id + '.webm')):
            path = os.path.join(path, video_id + '.webm')
        elif os.path.isfile(os.path.join(path, video_id + '.mp4')):
            path = os.path.join(path, video_id + '.mp4')
        else:
            return

        data = {'thumbnail_url': info_dict['thumbnail'], "path": path}
        return data
