from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Category


class CategorySerializer(ModelSerializer):
    verbose = SerializerMethodField('get_verbose')

    class Meta:
        model = Category
        fields = ('pk', 'name', 'verbose')

    def get_verbose(self, obj):
        lang = self.context.get('lang')
        if lang == "en":
            return obj.english
        elif lang == "ru":
            return obj.russian
        return obj.turkmen
