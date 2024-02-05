from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Icon
from files.serializers import IconSerializer


@api_view(('GET',))
@cache_page(settings.CACHE_TTL)
@csrf_exempt
def icons(request):
    """
    View function to get all icons.
    """
    lang = request.GET.get('lang')
    queryset = Icon.objects.all()
    serializer = IconSerializer(queryset, many=True, context={"lang": lang})

    return Response(serializer.data)
