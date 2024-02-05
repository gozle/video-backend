from datetime import datetime, timedelta

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from files.models import Video
from files.serializers import VideoSerializer


@api_view(('GET',))
@csrf_exempt
def popular_videos(request):
    # apply geo block
    if request.GET.get('geo_block'):
        return HttpResponse()

    # Get date to get popular video from
    time = int(request.GET.get('time'))
    ago = datetime.now() - timedelta(time)

    # Queryset and Pagination
    queryset = Video.objects.exclude(m3u8=None).filter(
        date__gte=ago).order_by('-view')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)

    # Return data
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
