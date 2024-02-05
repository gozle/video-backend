from itertools import chain

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import Serializer

from files.serializers import VideoSerializer, AdSerializer


class CombinedSerializer(Serializer):
    data = SerializerMethodField('get_data')

    def get_data(self, obj):
        video = VideoSerializer(obj['video_data'], many=True, context=self.context).data
        ad = AdSerializer(obj['ad_data'], context=self.context).data
        return list(chain([ad], video))
