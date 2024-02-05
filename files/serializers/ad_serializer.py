from django.conf import settings
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Ad

DOMAIN = settings.DOMAIN


class AdSerializer(ModelSerializer):
    description = SerializerMethodField('get_description')
    contacts = SerializerMethodField('get_contacts')
    title = SerializerMethodField('get_title')
    m3u8 = SerializerMethodField('get_m3u8')
    thumbnail_url = SerializerMethodField('get_thumbnail')

    class Meta:
        model = Ad
        fields = ('pk', 'title', 'description', 'duration',
                  'm3u8', 'link', 'thumbnail_url', 'contacts')

    def get_description(self, obj):
        if self.context.get('lang') == 'en':
            return obj.description_en
        if self.context.get('lang') == 'ru':
            return obj.description_ru
        return obj.description_tm

    def get_m3u8(self, obj):
        if self.context.get('lang') == 'en':
            if obj.m3u8_en:
                return DOMAIN+obj.m3u8_en
            else:
                return None
        elif self.context.get('lang') == 'ru':
            if obj.m3u8_ru:
                return DOMAIN+obj.m3u8_ru
            else:
                return None
        if obj.m3u8_tm:
            return DOMAIN+obj.m3u8_tm
        return None

    def get_thumbnail(self, obj):
        if self.context.get('lang') == 'en':
            if obj.thumbnail_en:
                return DOMAIN+obj.thumbnail_en.url
        elif self.context.get('lang') == 'ru':
            if obj.thumbnail_ru:
                return DOMAIN+obj.thumbnail_ru.url
        else:
            if obj.thumbnail_tm:
                return DOMAIN+obj.thumbnail_tm.url

    def get_title(self, obj):
        if self.context.get('lang') == 'en':
            return obj.title_en
        if self.context.get('lang') == 'ru':
            return obj.title_ru
        return obj.title_tm

    @staticmethod
    def get_contacts(obj):
        names = []
        for item in obj.contacts.all():
            names.append({'pk': item.pk, 'name': item.name,
                         'icon': DOMAIN+item.icon.url, 'info': item.information})
        return names
