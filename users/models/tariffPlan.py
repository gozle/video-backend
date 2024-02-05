from django.db import models


# TariffPlan model
class TariffPlan(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    can_download = models.BooleanField(default=False)
    less_ad = models.BooleanField(default=False)
    live_videos = models.BooleanField(default=False)
    premium_channels = models.BooleanField(default=False)

    def __str__(self):
        return self.name
