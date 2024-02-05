from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Icon
from tmtubBackend import settings

DOMAIN = settings.DOMAIN


class IconSerializer(ModelSerializer):
    category_icon = SerializerMethodField('get_icon')
    category_slug = SerializerMethodField('get_slug')
    category_name = SerializerMethodField('get_name')

    class Meta:
        model = Icon
        fields = ('pk', 'category_slug', 'category_icon', 'category_name')

    @staticmethod
    def get_icon(obj):
        if obj.icon:
            return DOMAIN+obj.icon.url

    @staticmethod
    def get_slug(obj):
        return obj.slug

    def get_name(self, obj):
        lang = self.context.get('lang')
        if lang == 'en':
            return obj.english
        elif lang == 'ru':
            return obj.russian
        return obj.turkmen
