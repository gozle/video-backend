import os
import re
from datetime import datetime
import subprocess
import time

from django import db
from django.conf import settings
import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size
import subprocess
import json

import requests


def remove_emojis(data):
    """Function to remove emojis from a string."""
    emoji = re.compile("["
                       u"\U0001F600-\U0001F64F"  # emoticons
                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                       u"\U00002500-\U00002BEF"  # chinese char
                       u"\U00002702-\U000027B0"
                       u"\U00002702-\U000027B0"
                       u"\U000024C2-\U0001F251"
                       u"\U0001f926-\U0001f937"
                       u"\U00010000-\U0010ffff"
                       u"\u2640-\u2642"
                       u"\u2600-\u2B55"
                       u"\u200d"
                       u"\u23cf"
                       u"\u23e9"
                       u"\u231a"
                       u"\ufe0f"  # dingbats
                       u"\u3030"
                       "]+", re.UNICODE)
    return re.sub(emoji, '', data)


def get_duration(duration):
    """Function to convert duration to seconds."""
    duration = duration.replace('PT', '')
    duration = '0:'+duration if len(duration.split(':')) == 2 else duration
    duration = '0:0:'+duration if len(duration.split(':')) == 1 else duration
    date = datetime.strptime(duration, '%H:%M:%S')
    seconds = date.hour*60*60 + date.minute * 60 + date.second
    return seconds


def to_hls(input, output):
    """Function to convert mp4 to hls."""
    video = ffmpeg_streaming.input(input)
    _360p = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
    _480p = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))
    _720p = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))
    _1080p = Representation(Size(1920, 1080), Bitrate(4096 * 1024, 320 * 1024))

    hls = video.hls(Formats.h264())
    hls.representations(_360p, _480p, _720p, _1080p)
    hls.output(output+'video.m3u8')


def get_dar(filename):
    """Function to get a display aspect ratio."""
    # Run FFprobe command to get JSON output
    cmd = ['ffprobe', '-v', 'quiet', '-print_format',
           'json', '-show_streams', filename]
    output = subprocess.check_output(cmd)

    # Parse JSON output to find a display aspect ratio
    data = json.loads(output.decode('utf-8'))
    for stream in data['streams']:
        if stream.get('display_aspect_ratio'):
            return stream['display_aspect_ratio']
        else:
            print(stream)
    # If a display aspect ratio not found, return default value
    return '16:9'


def convert_ad(ad, media_root):
    """
    Convert an ad to HLS format.

    Args:
        media_root: The MEDIA_ROOT directory.
        ad: The ad to convert.
    """
    # Check if the m3u8 file is empty or missing.
    if ad.m3u8_en == '' or ad.m3u8_en is None:
        # Get the input path.
        input_path = ad.video_en.path

        # Create the output path.
        output_path = os.path.join(
            os.path.dirname(input_path),
            str(ad.id),
            'en',
        )

        # Print the input path.
        print('[INPUT]', input_path)

        # Convert the video file to HLS.
        to_hls(input_path, output_path)

        # Set the m3u8 file for the ad.
        ad.m3u8_en = '/media' + \
            output_path.split(media_root)[-1] + 'video.m3u8'

        print('[OUTPUT]', output_path)

    # Repeat the same steps for the other languages.
    if ad.m3u8_tm == '' or ad.m3u8_tm is None:
        input_path = ad.video_tm.path
        output_path = os.path.join(
            os.path.dirname(input_path),
            str(ad.id),
            'tm',
        )
        print('[INPUT]', input_path)
        to_hls(input_path, output_path)
        ad.m3u8_tm = '/media' + \
            output_path.split(media_root)[-1] + 'video.m3u8'
        print('[OUTPUT]', output_path)

    if ad.m3u8_ru == '' or ad.m3u8_ru is None:
        input_path = ad.video_ru.path
        output_path = os.path.join(
            os.path.dirname(input_path),
            str(ad.id),
            'ru',
        )
        print('[INPUT]', input_path)
        to_hls(input_path, output_path)
        ad.m3u8_ru = '/media' + \
            output_path.split(media_root)[-1] + 'video.m3u8'
        print('[OUTPUT]', output_path)

    db.connections.close_all()

    # Save the ad to the database.
    ad.save()

    # Sleep for 2 seconds to prevent overloading the server.
    time.sleep(2)


def get_best_video(formats):
    """
    Returns the best video format from a list of formats.

    Args:
      formats: A list of dictionaries, each of which represents a video format.

    Returns:
      The best video format, or None if no video format meets the criteria.
    """

    best_video = None
    for format in formats:
        if (format.get('vcodec') and format['vcodec'] != 'none') and (not format.get('acodec') or format['acodec'] == 'none'):
            if best_video is None or format['height'] > best_video['height'] and format['height'] <= 1080:
                best_video = format

    return best_video


def get_best_audio(formats, video_ext):
    """
    Returns the best audio format from a list of formats.

    Args:
      formats: A list of dictionaries, each of which represents a video format.
      video_ext: The extension of the video file.

    Returns:
      The best audio format, or None if no audio format meets the criteria.
    """

    best_audio = None
    for format in formats:
        if (format.get('acodec') and format['acodec'] != 'none') and (not format.get('vcodec') or format['vcodec'] == 'none') and format['ext'] == video_ext:
            best_audio = format

    return best_audio
