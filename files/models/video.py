from datetime import datetime

import pytz
from django.db import models

from files.models import Category, Channel, Playlist
from users.models import User


class Video(models.Model):
    TYPE_CHOICES = (('video', 'Video'), ('shorts', 'Shorts'),)

    video_id = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    m3u8 = models.CharField(max_length=500, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/%d', null=True)
    subtitle = models.FileField(
        upload_to='subtitles/%d', null=True, blank=True)
    view = models.IntegerField(default=0, blank=True)

    # TODO: Remove this category field, because channel already has this field.
    category = models.ManyToManyField(
        Category, blank=True, related_name='videos')
    video = models.FileField(upload_to='video/')
    type = models.CharField(
        max_length=6, choices=TYPE_CHOICES, default='video')

    date = models.DateTimeField(auto_now_add=True)
    published_at = models.DateField(null=True, blank=True)

    duration = models.IntegerField(blank=True, null=True)
    expansion = models.CharField(max_length=50, null=True, blank=True)
    expansion_m = models.CharField(
        max_length=10, default='16:9', null=True,  blank=True)

    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')

    ignore_users = models.ManyToManyField(User, related_name='ignored_videos', blank=True)

    premium = models.BooleanField(default=False, blank=True)

    is_processing = models.BooleanField(default=False)
    server = models.IntegerField(default=1, blank=True)
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# TODO: Make this to delete existing video files when video is deleted.

#    def delete(self, *args, **kwargs):
#        try:
#            path = self.thumbnail.path.split('thumbnails')[0]
#            path = path+'videos/'+str(self.id)
#            print('[DELETED]', path)
#            shutil.rmtree(path)
#            if self.thumbnail:
#                os.remove(self.thumbnail.path)
#            super(Video, self).delete(*args, **kwargs)
#        except Exception as e:
#            print('[ERROR]', e)

# @receiver(post_delete)
# def delete_videos(sender, instance, **kwargs):
#     try:
#         path = instance.thumbnail.path.split('thumbnails')[0]
#         path = path+'videos/'+str(instance.id)
#         print('[DELETED]', path)
#         shutil.rmtree(path)
#     except Exception as e:
#         print('[ERROR]', e)
