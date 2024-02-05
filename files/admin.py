from django.contrib import admin

from files.models import Video, Category


class VideoAdmin(admin.ModelAdmin):
    search_fields = ['title']


# Register your models here.
admin.site.register(Video, VideoAdmin)
admin.site.register(Category)
