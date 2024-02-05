from django.db import models


class Icon(models.Model):
    slug = models.CharField(max_length=200)
    icon = models.FileField(upload_to='icons')
    turkmen = models.CharField(max_length=200)
    english = models.CharField(max_length=200)
    russian = models.CharField(max_length=200)

    def __str__(self):
        return self.slug
