from django.db import models

from files.models import Video
from users.models import User


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
