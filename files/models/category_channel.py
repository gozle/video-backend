from django.db import models


class Category_Channel(models.Model):
    name = models.CharField(max_length=100)
    turkmen = models.CharField(max_length=150)
    english = models.CharField(max_length=150)
    russian = models.CharField(max_length=150)

    def __str__(self):
        return self.name
