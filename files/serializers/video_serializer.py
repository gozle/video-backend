from django.conf import settings
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from files.models import Video, Like
from files.serializers.category_serializer import CategorySerializer

DOMAIN = settings.DOMAIN


class VideoSerializer(ModelSerializer):
    thumbnail_url = SerializerMethodField('get_thumbnail_url')
    channel_name = SerializerMethodField('get_channel_name')
    channel_url = SerializerMethodField('get_channel_avatar')
    channel_id = SerializerMethodField('get_channel_id')
    category = SerializerMethodField('get_category_names')
    m3u8 = SerializerMethodField('get_m3u8')
    date = SerializerMethodField('get_date')
    live = SerializerMethodField('get_live')
    is_subscribed = SerializerMethodField("get_is_subscribed")
    is_liked = SerializerMethodField("get_is_liked")
    likes_count = SerializerMethodField("get_likes_count")

    class Meta:
        model = Video
        fields = ('pk', 'title', 'description', 'view', 'duration', 'm3u8', 'expansion',
                  'thumbnail_url', 'category', 'live', 'date', 'channel_name', 'channel_url', 'channel_id',
                  "is_subscribed", "is_liked", "likes_count")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'remove_fields' in self.context:
            remove_fields = self.context['remove_fields']
            for field_name in remove_fields:
                self.fields.pop(field_name)

    @staticmethod
    def get_m3u8(obj):
        domain = DOMAIN if obj.server == 1 else DOMAIN + '/' + str(obj.server)
        if obj.m3u8:
            return domain + obj.m3u8 if 'https://' not in obj.m3u8 else obj.m3u8

    @staticmethod
    def get_thumbnail_url(obj):
        if obj.thumbnail:
            return DOMAIN + obj.thumbnail.url if obj.server == 1 else DOMAIN + '/' + str(obj.server) + obj.thumbnail.url
        return None

    @staticmethod
    def get_channel_name(obj):
        return obj.channel.name

    @staticmethod
    def get_channel_id(obj):
        return obj.channel.pk


    @staticmethod
    def get_channel_avatar(obj):
        if obj.channel.avatar:
            return DOMAIN + obj.channel.avatar.url if obj.channel.server == 1 else DOMAIN + '/' + str(
                obj.channel.server) + obj.channel.avatar.url

    def get_category_names(self, obj):
        return CategorySerializer(obj.channel.categories.all(), many=True, context=self.context).data

    @staticmethod
    def get_date(obj):
        if obj.published_at:
            return obj.published_at
        else:
            return obj.date

    @staticmethod
    def get_live(obj):
        if obj.category.filter(name='live').exists():
            return True
        return False

    def get_is_subscribed(self, obj):
        if self.context.get("user"):
            return self.context.get("user") in obj.channel.subscribers.all()
        return False

    def get_is_liked(self, obj):
        if self.context.get("user"):
            return Like.objects.filter(user=self.context.get("user"), video=obj).exists()
        return False

    def get_likes_count(self, obj):
        return Like.objects.filter(video=obj).count()
