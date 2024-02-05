from django.conf import settings
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from files.models import Comment

DOMAIN = settings.DOMAIN


class CommentSerializer(ModelSerializer):
    user = SerializerMethodField('get_user')

    class Meta:
        model = Comment
        fields = ('pk', 'user', 'text', 'created_at')

    @staticmethod
    def get_user(obj):
        data = {'pk': obj.user.pk, 'username': obj.user.username,
                'avatar': DOMAIN + obj.user.avatar.url if obj.user.avatar else None}

        return data
