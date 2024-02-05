from django.db import models

from files.models import Category


class ChannelToDownload(models.Model):
    link = models.CharField(max_length=400)
    categories = models.ManyToManyField(Category)
    all_video = models.BooleanField(default=False, blank=True)
    server = models.IntegerField(default=0, blank=True)
    is_processing = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.link
