from django.db import models
from django.core.exceptions import ValidationError


# Configurations for OAuth 2.0 client.
class Client(models.Model):
    client_id = models.CharField(max_length=250)
    client_secret = models.CharField(max_length=250)

    callback_uri = models.CharField(max_length=250)

    login_uri = models.CharField(max_length=250)
    token_uri = models.CharField(max_length=250)
    resource_uri = models.CharField(max_length=250)

    def save(self, *args, **kwargs):
        using = kwargs.get('using') or 'default'
        if not self.pk and Client.objects.using(using).exists():
            # if you'll not check for self.pk
            # then error will also be raised in the update of exists model
            raise ValidationError('There is can be only one client instance')
        return super(Client, self).save(*args, **kwargs)
