from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from files.models import Video
from files.serializers import VideoSerializer


@api_view(('GET',))
@csrf_exempt
def latest_videos(request):
    # apply geo block
    if request.GET.get('geo_block'):
        return HttpResponse()
    """
    View function to get the latest added videos
    """
    # Get objects ordered by published date.
    queryset = Video.objects.exclude(m3u8='').exclude(m3u8=None).order_by('-published_at')

    # Paginate and return
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount', 10)
    result_page = paginator.paginate_queryset(queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
