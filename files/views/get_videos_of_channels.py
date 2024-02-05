from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from files.models import Channel
from files.serializers import VideoSerializer


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
@csrf_exempt
def get_videos_of_channel(request, pk):
    """
    Return a list of videos of a channel

    Args:
        request: Request objects
        pk: ID of the channel

    Returns:
        Response objects
    """
    # Define sort options with GET parameters
    sort = request.GET.get('sort')
    sort = {'view': 'view', 'date': 'published_at', 'random': 'random'}[sort]
    order = request.GET.get('order')
    order = {'asc': '', 'desc': '-'}[order]

    # Get channel object
    objects = Channel.objects.get(pk=pk)
    objects.view += 1
    objects.save()
    if sort == 'random':
        videos = objects.videos.exclude(
            m3u8='').exclude(m3u8=None).order_by('?')
    else:
        videos = objects.videos.exclude(m3u8='').exclude(
            m3u8=None).order_by(order+sort)

    # apply geo block
    if request.GET.get('geo_block'):
        videos = videos.filter(channel__geo_protected=False)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(queryset=videos, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
                                 "lang": request.GET.get('lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)