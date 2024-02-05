from django.conf import settings
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from files.models import Video
from files.serializers.category_serializer import CategorySerializer

DOMAIN = settings.DOMAIN


class VideoSerializer(ModelSerializer):
    thumbnail_url = SerializerMethodField('get_thumbnail_url')
    category = SerializerMethodField('get_category_names')
    m3u8 = SerializerMethodField('get_m3u8')
    date = SerializerMethodField('get_date')

    class Meta:
        model = Video
        fields = ('pk', 'title', 'description', 'view', 'm3u8', 'expansion',
                  'thumbnail_url', 'category', 'date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'remove_fields' in self.context:
            remove_fields = self.context['remove_fields']
            for field_name in remove_fields:
                self.fields.pop(field_name)

    def get_category_names(self, obj):
        return CategorySerializer(obj.channel.categories.all(), many=True, context=self.context).data

    @staticmethod
    def get_m3u8(obj):
        domain = DOMAIN if obj.server == 1 else DOMAIN + '/' + str(obj.server)
        if obj.m3u8:
            return domain + obj.m3u8 if 'https://' not in obj.m3u8 else obj.m3u8

    @staticmethod
    def get_thumbnail_url(obj):
        if obj.thumbnail:
            return DOMAIN + '/film' + obj.thumbnail.url
        return None

    @staticmethod
    def get_date(obj):
        if obj.published_at:
            return obj.published_at
        else:
            return obj.date
