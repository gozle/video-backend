from django.contrib import admin

from files.models import Video, Ad, Channel, Category, Icon, ChannelToDownload, Playlist, AdContact


class VideoAdmin(admin.ModelAdmin):
    search_fields = ['title']


class VideoInline(admin.TabularInline):
    model = Video


class ChannelAdmin(admin.ModelAdmin):
    search_fields = ['pk', 'name']


# Register your models here.
admin.site.register(Video, VideoAdmin)
admin.site.register(Ad)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Category)
admin.site.register(Icon)
admin.site.register(ChannelToDownload)
admin.site.register(Playlist)
admin.site.register(AdContact)
