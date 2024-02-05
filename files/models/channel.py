import os

from django.db import models

from files.models import Category
from users.models import User


class Channel(models.Model):
    channel_id = models.CharField(max_length=40)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='channels')
    avatar = models.ImageField(upload_to='avatar/%d', null=True, blank=True)
    banner = models.ImageField(upload_to='banner/%d', null=True, blank=True)
    all_video = models.BooleanField(default=False, blank=True)

    view = models.IntegerField(default=0)
    server = models.IntegerField(default=1, blank=True)
    last_checked = models.DateTimeField(auto_now_add=True)

    premium = models.BooleanField(default=False, blank=True)

    subscribers = models.ManyToManyField(
        User, related_name='subscriptions', blank=True)

    geo_protected = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )

    def delete(self, *args, **kwargs):
        def delete_file(path):
            if os.path.isfile(path):
                os.remove(path)

        if self.avatar:
            delete_file(self.avatar.path)

        if self.banner:
            delete_file(self.banner.path)
        super(Channel, self).delete(*args, **kwargs)
