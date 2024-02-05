from django.db import models


class Ad(models.Model):
    CATEGORY_CHOICES = (('video', 'video'), ('home', 'home'),)

    title_tm = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)

    description_en = models.TextField(null=True, blank=True)
    description_tm = models.TextField(null=True, blank=True)
    description_ru = models.TextField(null=True, blank=True)

    duration = models.IntegerField(blank=True, null=True)

    thumbnail_en = models.ImageField(upload_to='thumbnails/%d')
    thumbnail_tm = models.ImageField(
        upload_to='thumbnails/%d', blank=True, null=True)
    thumbnail_ru = models.ImageField(
        upload_to='thumbnails/%d', blank=True, null=True)

    link = models.URLField()

    m3u8_en = models.CharField(max_length=500, null=True, blank=True)
    m3u8_tm = models.CharField(max_length=500, null=True, blank=True)
    m3u8_ru = models.CharField(max_length=500, null=True, blank=True)

    view = models.IntegerField(default=0)
    click = models.IntegerField(default=0)

    video_en = models.FileField(upload_to='ads/', null=True, blank=True)
    video_tm = models.FileField(upload_to='ads/', null=True, blank=True)
    video_ru = models.FileField(upload_to='ads/', null=True, blank=True)

    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default='video')
    is_active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.title_en
