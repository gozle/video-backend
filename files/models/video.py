import random
import string
from django.db import models
from files.models import Category


def id_generator(size=15, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Video(models.Model):
    video_id = models.CharField(default=id_generator, max_length=30)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    m3u8 = models.CharField(max_length=500, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/%d', null=True)
    view = models.IntegerField(default=0, blank=True)

    category = models.ManyToManyField(
        Category, blank=True, related_name='videos')

    date = models.DateTimeField(auto_now_add=True)
    published_at = models.DateField(null=True, blank=True)

    expansion = models.CharField(max_length=50, null=True, blank=True)
    expansion_m = models.CharField(
        max_length=10, default='16:9', null=True,  blank=True)

    server = models.IntegerField(default=5, blank=True)

    def __str__(self):
        return self.title
