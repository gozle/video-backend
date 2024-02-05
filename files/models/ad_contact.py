from django.db import models

from files.models import Ad


class AdContact(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    icon = models.FileField(upload_to='icons')
    information = models.CharField(max_length=400, null=True, blank=True)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE,
                           related_name='contacts')
