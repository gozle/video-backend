from django.db import models
from django.utils import timezone
from files.models import Video
from users.models import User


class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index('viewed_at', name='viewed_at_idx'),
        ]
        ordering = ['-viewed_at']

    def save(self, *args, **kwargs):
        if not self.id:
            self.viewed_at = timezone.now()
        return super(VideoView, self).save(*args, **kwargs)
