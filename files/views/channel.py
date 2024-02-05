from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Channel
from files.serializers import ChannelSerializer


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
@csrf_exempt
def channel(request):
    """
    View function for get channel details
    """
    queryset = Channel.objects.get(pk=request.GET.get('pk'))
    serializer = ChannelSerializer(queryset)
    return Response(serializer.data)
