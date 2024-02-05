from django.conf import settings
from django.db import models

from files.models import Channel


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=100)
    title = models.CharField(max_length=400)
    thumbnail = models.ImageField(upload_to="thumbnails/%d", null=True)
    view = models.IntegerField(default=0, blank=True)

    server = models.IntegerField(default=settings.SERVER, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name='playlists')

    def __str__(self):
        return self.title
