from django.contrib import admin

from users.models import User, Client, TariffPlan, TariffSubscription

# Register your models here.
admin.site.register(User)
admin.site.register(Client)
admin.site.register(TariffPlan)
admin.site.register(TariffSubscription)
