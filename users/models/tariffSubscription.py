import uuid
from datetime import timedelta, datetime
from django.db import models

from users.models import TariffPlan


# Model for tariff subscriptions
class TariffSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(TariffPlan, on_delete=models.CASCADE, related_name="tariff_subscriptions")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="tariff_subscriptions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        # Return the tariff name and the username
        return f"{self.plan.name} - {self.user.username}"

    def is_active(self):
        if datetime.now() < self.expires_at and self.active:
            return True
        else:
            return False

    def activate(self):
        self.active = True
        self.expires_at = datetime.now() + timedelta(days=30)
        self.save()
