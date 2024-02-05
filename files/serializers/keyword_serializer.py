from rest_framework.serializers import ModelSerializer

from users.models import Keyword


class KeywordSerializer(ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('pk', 'keyword')
