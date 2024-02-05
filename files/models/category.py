from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)
    turkmen = models.CharField(max_length=150)
    english = models.CharField(max_length=150)
    russian = models.CharField(max_length=150)

    def __str__(self):
        return self.name
