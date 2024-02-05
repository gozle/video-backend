from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=250, unique=True)
    user_id = models.CharField(max_length=250, unique=True)
    first_name = models.CharField(max_length=250, null=True, blank=True)
    last_name = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/%M/%d", null=True, blank=True)

    history = models.ManyToManyField('files.Video')
    user_views = models.ManyToManyField('files.Video', through='files.VideoView', related_name='user_views')
    keyword_history = models.ManyToManyField("users.Keyword")

    access_token = models.CharField(max_length=250, null=True, blank=True)
    refresh_token = models.CharField(max_length=250, null=True, blank=True)

    source = models.CharField(max_length=250, default="Gozle ID", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.username
