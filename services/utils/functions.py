import json
import os
import re
import subprocess
from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from redis import Redis


def find_object_by_id(array, id, default):
    for obj in array:
        if obj.get('id') == id:
            return obj
    return default


def get_keys_from_redis():
    redis = Redis()
    values = []

    keys = redis.keys('*')
    for key in keys:
        values.append({"id": key.decode(), "metadata": redis.get(key).decode()})
    return values


def is_already_added(key):
    ids = [i['id'] for i in get_keys_from_redis()]
    if key in ids:
        return True
    return False


def get_best_video(formats):
    best_video = None
    for format in formats:
        if (format.get('vcodec') and format['vcodec'] != 'none') and (
                not format.get('acodec') or format['acodec'] == 'none'):
            if best_video is None or best_video['height'] < format['height'] <= 1080:
                best_video = format

    return best_video


def get_best_audio(formats, video_ext):
    best_audio = None
    for format in formats:
        if (format.get('acodec') and format['acodec'] != 'none') and (
                not format.get('vcodec') or format['vcodec'] == 'none') and format['ext'] == video_ext:
            best_audio = format

    return best_audio


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


def download_image(url):
    file_temp = NamedTemporaryFile()
    file_temp.write(urlopen(url).read())
    file_temp.flush()

    return File(file_temp)


def get_from_local(path):
    if os.path.isfile(path + '.webm'):
        path = path + '.webm'
    elif os.path.isfile(path + '.mp4'):
        path = path + '.mp4'
    return File(open(path, 'rb'))


def get_dar(filename):
    """Function to get a display aspect ratio."""
    # Run FFprobe command to get JSON output
    cmd = ['ffprobe', '-v', 'quiet', '-print_format',
           'json', '-show_streams', filename]
    output = subprocess.check_output(cmd)

    # Parse JSON output to find a display aspect ratio
    data = json.loads(output.decode('utf-8'))
    for stream in data['streams']:
        if stream.get('width') and stream.get('height'):
            width = stream.get('width')
            height = stream.get('height')
            if width >= height:
                return '16:9'
            else:
                return '9:16'
    # If a display aspect ratio not found, return default value
    return '16:9'
