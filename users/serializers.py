from rest_framework import serializers

from users.models import User, TariffPlan

DOMAIN = 'https://v.gozle.com.tm/'


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField('get_avatar')

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'avatar', 'source', 'created_at',
            'updated_at')

    @staticmethod
    def get_avatar(obj):
        if obj.avatar:
            return DOMAIN + obj.avatar.url
        else:
            return None


class TariffPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlan
        fields = "__all__"


