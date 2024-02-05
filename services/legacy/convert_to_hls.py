import os, sys
import django
from django.utils import timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()
from files.models import Video, Ad
from django.conf import settings
from django.db.models import Q
from assets.functions.functions import to_hls, convert_ad
from django.db import models
import time


# TODO: Refactor this function.

def convert_video():
    while True:
        # Get all ads that don't have a m3u8 file.
        if settings.SERVER == 1:
            to_convert = Ad.objects.exclude(category='home').filter(
                models.Q(m3u8_en__isnull=True) | models.Q(m3u8_en__exact='') |
                models.Q(m3u8_tm__isnull=True) | models.Q(m3u8_tm__exact='') |
                models.Q(m3u8_ru__isnull=True) | models.Q(m3u8_ru__exact='')
            )
            if to_convert.exists():
                try:
                    to_convert = to_convert[0]
                    convert_ad(to_convert, settings.MEDIA_ROOT)
                except ValueError:
                    print('[CANt FIND VIDEO]', to_convert.title_en)
                except Exception as e:
                    print(e)
                    time.sleep(2)
                    continue

        try:
            to_convert = Video.objects.filter(Q(is_processing=False, server=settings.SERVER) & Q(m3u8=None)).order_by("-channel__view")[0]
        except:
            print("Cant find video, searching...")
            time.sleep(5)
            continue

        try:
            print("[Video got]")
            input_path = to_convert.video.path
            output_path = '/'.join(input_path.split('/')
                                   [0:-1])+'/'+to_convert.video_id+'/'
            print('[INPUT]', input_path)
            to_convert.is_processing = True
            to_convert.save()
            to_hls(input_path, output_path)
            to_convert.m3u8 = '/media/' + \
                output_path.split(settings.MEDIA_ROOT)[-1]+'video.m3u8'
            to_convert.date = timezone.now()
            to_convert.save()
            to_convert.video.delete(save=True)
            print('[OUTPUT]', output_path)
            time.sleep(2)
        except ValueError:
            print("[CAN'T FIND VIDEO]", to_convert.title)
            to_convert.delete()
            time.sleep(2)
        except Exception as e:
            print(e)
            time.sleep(2)
            continue


convert_video()
