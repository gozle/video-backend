import os

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Channel
from django.conf import settings

from files.serializers.category_serializer import CategorySerializer

DOMAIN = settings.DOMAIN


class ChannelSerializer(ModelSerializer):
    channel_avatar = SerializerMethodField('get_channel_avatar')
    channel_banner = SerializerMethodField('get_channel_banner')
    video_count = SerializerMethodField('get_video_count')
    categories = SerializerMethodField("get_categories")
    is_subscribed = SerializerMethodField('get_is_subscribed')

    class Meta:
        model = Channel
        fields = ('pk', 'name', 'channel_avatar', 'view', 'description',
                  'channel_banner', 'video_count', "categories", "is_subscribed")

    @staticmethod
    def get_channel_avatar(obj):
        if obj.avatar:
            if obj.server == 1:
                return DOMAIN + obj.avatar.url
            else:
                if os.path.isfile(obj.avatar.path):
                    return DOMAIN + obj.avatar.url
                else:
                    return DOMAIN + '/' + str(obj.server) + obj.avatar.url

    @staticmethod
    def get_channel_banner(obj):
        if obj.banner:
            return DOMAIN + obj.banner.url if obj.server == 1 else DOMAIN + '/' + str(obj.server) + obj.banner.url

    @staticmethod
    def get_video_count(obj):
        return len(obj.videos.all())

    def get_categories(self, obj):
        return CategorySerializer(obj.categories.all(), many=True).data

    def get_is_subscribed(self, obj):
        if self.context.get("user"):
            return self.context.get("user") in obj.subscribers.all()
        return None