from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Video, Channel
from files.serializers import VideoSerializer


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
@csrf_exempt
def latest_videos(request):
    """
    View function to get the latest added videos
    """
    # Get objects ordered by published date.
    queryset = Video.objects.exclude(m3u8='').exclude(m3u8=None).order_by('-published_at')

    # apply geo block
    if request.GET.get('geo_block'):
        queryset = queryset.filter(channel__geo_protected=False)

    # Paginate and return
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount', 10)
    result_page = paginator.paginate_queryset(queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
