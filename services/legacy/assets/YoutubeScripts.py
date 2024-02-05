import datetime
import os
import requests
from vtt_to_srt.vtt_to_srt import ConvertFile
from yt_dlp import YoutubeDL
from services.legacy.assets.functions.functions import get_best_audio, get_best_video, remove_emojis
from youtubesearchpython import Channel, playlist_from_channel_id
from pytube import Playlist


class YT:
    def __init__(self):
        pass

    @staticmethod
    def get_channel(link):
        """
        Function for getting channel details.
        Args:
            link: The YouTube link of channel

        Returns:
            metadata:
                id: ID of a channel.
                title: Title of channel.
                description: Description of a channel.
                avatar_url: Avatar url of a channel.
                banner_url: Banner url of a channel.
                keyword: Keywords of a channel separated with spaces.
        """
        channel = Channel.get(link)
        metadata = dict()
        metadata['id'] = channel['id']
        metadata['title'] = channel['title']
        metadata['description'] = remove_emojis(channel['description'])
        metadata['avatar_url'] = channel['thumbnails'][2]['url']
        metadata['banner_url'] = channel['banners'][0]['url'] if \
            channel['banners'] else None
        metadata['keywords'] = channel['keywords']
        return metadata

    @staticmethod
    def get_playlists_from_channel(channel_id):
        """
        Function for getting playlists of a channel.
        Args:
            channel_id: ID of a channel.

        Returns:
            playlists:
                metadata:
                    id: ID of a playlist.
                    title: Title of a playlist.
                    thumbnail_url: Thumbnail url of a playlist.
                    channel: ID of a channel.
        """
        playlists = []
        # Get playlists of a channel
        channel = Channel(channel_id)
        while channel.has_more_playlists():
            channel.next()
        for playlist_data in channel.result['playlists']:
            metadata = dict()
            metadata['id'] = playlist_data['id']
            metadata['title'] = playlist_data['title']
            metadata['thumbnail_url'] = playlist_data['thumbnails'][0]['url']
            metadata['channel'] = channel_id
            playlists.append(metadata)
        return playlists

    @staticmethod
    def get_videos_from_playlist(playlist_id, all_videos):
        """
        Function for signing videos of a given video list with a playlist.
        Args:
            playlist_id: ID of playlists.
            all_videos: All video list.

        Returns:
            all_videos: Signed with playlist.
        """
        # Get playlist
        playlist = Playlist('https://www.youtube.com/playlist?list=' + playlist_id)
        for video in playlist.videos:
            for video_metadata in all_videos:
                # Check video is in playlist
                if video_metadata['id'] == video.video_id:
                    video_metadata['playlist'] = playlist_id
            if video.video_id not in all_videos:
                # If playlists video is not in the video list, add it
                all_videos.append({'id': video.video_id, 'playlist': playlist_id})
        return all_videos

    @staticmethod
    def get_all_videos_from_channel(channel_id):
        """
        Function for getting all videos of a channel.
        Args:
            channel_id: ID of a channel.

        Returns:
            List of videos of a channel.
        """
        channel = Playlist(playlist_from_channel_id(channel_id))
        videos = []
        for video in channel.videos:
            videos.append({'id': video.video_id, 'playlist': None})
        return videos

    @staticmethod
    def detect_language(captions):
        """
        Function for detecting original language of captions.
        Args:
            captions: The lang list of captions.

        Returns:
            Original language of captions.
        """
        lang = [lang for lang in captions if
                'orig' in lang or len(lang.split('-')) > 1 and lang.split('-')[0] == lang.split('-')[1]]

        return lang[0] if len(lang) else None

    @staticmethod
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

    @staticmethod
    def filter_by_duration(info, *, incomplete):
        # TODO: Check this filter
        duration = info.get('duration')
        # If duration is more than 3600 seconds, return none
        if duration and duration > 3600:
            print('[DURATION IS TOO LARGE]')
            return None

    def download_video(self, video_id, path, all_video):
        """
        Function to download a video.
        Args:
            video_id: ID of video.
            path: Path to be downloaded video.
            all_video: Download all videos or download only newer than 1 year.

        Returns:
            Metadata of the downloaded video.
        """
        # Set the video download options
        link = "https://youtube.com/watch?v=" + video_id
        ydl_opts = {"format": self.format_selector,  # This will select the specific resolution typed here
                    "outtmpl": path + video_id,
                    "quiet": True,
                    "match_filter": self.filter_by_duration
                    }
        with YoutubeDL(ydl_opts) as (ydl):
            # Extract information about the video
            info_dict = ydl.extract_info(link, download=False)
            metadata = dict()
            metadata['id'] = info_dict['id']
            metadata['title'] = info_dict['fulltitle']
            metadata['description'] = info_dict['description']
            metadata['duration'] = info_dict['duration']
            metadata['thumbnail_url'] = info_dict['thumbnail']
            metadata['published_at'] = info_dict['upload_date']

            # TODO: Change this video download conditions
            if all_video:
                ydl.download(link)
            else:
                if datetime.datetime.strptime(metadata['published_at'], '%Y%m%d') > \
                        datetime.datetime.now() - datetime.timedelta(days=365):
                    print(metadata["published_at"])
                    ydl.download(link)
                else:
                    return None

            # Check if the video is already downloaded
            if os.path.isfile(path+video_id+'.webm'):
                metadata['video'] = path + video_id + '.webm'
            elif os.path.isfile(path+video_id+'.mp4'):
                metadata['video'] = path + video_id + '.mp4'
            else:
                return

            # Get captions of video
            automatic_captions = info_dict.get('automatic_captions')
            if len(automatic_captions) != 0:
                lang = self.detect_language(automatic_captions)
                # Download captions
                if lang:
                    url = [item['url']
                           for item in automatic_captions[lang] if item['ext'] == 'vtt'][0]

                    with requests.get(url, stream=True) as r:
                        r.raise_for_status()
                        with open(path + video_id + '.vtt', 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)

                # Convert captions to srt
                    convert_file = ConvertFile(path + video_id + '.vtt', "utf-8")
                    convert_file.convert()
                    os.remove(path + video_id + '.vtt')
                    metadata['subtitle'] = path + video_id + '.srt'
            else:
                metadata['subtitle'] = None

        return metadata

    @staticmethod
    def get_thumbnail_url(video_id):
        """
        Function for getting thumbnail url of a video.
        Args:
            video_id: ID of video.

        Returns:
            Thumbnail url of video
        """
        link = "https://youtube.com/watch?v=" + video_id
        ydl_opts = {"quiet": True}
        with YoutubeDL(ydl_opts) as (ydl):
            info_dict = ydl.extract_info(link, download=False)
            thumbnail_url = info_dict['thumbnail']
            return thumbnail_url
