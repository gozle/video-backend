from datetime import datetime, timedelta

from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Video, Ad
from files.serializers import CombinedSerializer, VideoSerializer


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
@csrf_exempt
def popular_videos(request):
    # Get date to get popular video from
    time = int(request.GET.get('time'))
    ago = datetime.now() - timedelta(time)

    # Queryset and Pagination
    queryset = Video.objects.exclude(m3u8=None).filter(
        date__gte=ago).order_by('-view')

    # apply geo block
    if request.GET.get('geo_block'):
        queryset = queryset.filter(channel__geo_protected=False)

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)

    # If request source is mobile, add ad to response
    if request.GET.get('mob'):
        ad = Ad.objects.filter(category='home', is_active=True).order_by('?')
        if ad.exists():
            ad = ad[0]
            serializer = CombinedSerializer({'video_data': result_page, 'ad_data': ad}, context={"lang": request.GET.get(
                'lang'), 'mobile': 'True', 'remove_fields': ['category']})
            return paginator.get_paginated_response(serializer.data['data'])
    # Return data
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
