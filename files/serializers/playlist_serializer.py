from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Playlist
from django.conf import settings

from files.serializers import VideoSerializer

DOMAIN = settings.DOMAIN


class PlaylistSerializer(ModelSerializer):
    thumbnail = SerializerMethodField('get_thumbnail')
    videos_count = SerializerMethodField('get_videos_count')
    videos = SerializerMethodField('get_videos')

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'thumbnail', 'view', 'videos_count', 'videos')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'remove_fields' in self.context:
            remove_fields = self.context['remove_fields']
            for field_name in remove_fields:
                self.fields.pop(field_name)

    @staticmethod
    def get_thumbnail(obj):
        if obj.thumbnail:
            return DOMAIN + obj.thumbnail.url if obj.server == 1 else DOMAIN + '/' + str(obj.server) + obj.thumbnail.url
        else:
            return None

    @staticmethod
    def get_videos_count(obj):
        return len(obj.videos.all())

    @staticmethod
    def get_videos(obj):
        serializer = VideoSerializer(obj.videos.all(), many=True, context={
                                     'remove_fields': ['category', 'description', 'likes']})
        return serializer.data
