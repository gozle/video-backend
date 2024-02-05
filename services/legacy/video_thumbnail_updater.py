import django
import os

from services.utils.functions import download_image
from services.utils.tube import get_channel_metadata

os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()
from django.core.files import File
from urllib.request import urlopen
from files.models import Video, Channel
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings


channels = Channel.objects.filter(server=4).order_by('?')

for channel in channels:
    try:
        print("[CHANNEL GOT]", channel.name)
        metadata = get_channel_metadata(channel.channel_id)

        channel.avatar.save(str(channel.channel_id) + ".png", download_image(metadata.get('avatar')))
        if metadata.get('thumbnail'):
            channel.banner.save(str(channel.channel_id) + ".png", download_image(metadata.get('thumbnail')))

        channel.server = settings.SERVER
        channel.save()
        print('[Video Thumbnail Added]', channel.name)
    except Exception as e:
        print(e)
        continue
