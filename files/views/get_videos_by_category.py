from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Category, Video
from files.serializers import VideoSerializer


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
def get_videos_by_category(request):
    """
    View function to get videos from a specific category
    """
    # Get data from request
    pk = request.GET.get('pk')
    queryset = cache.get('random_category_'+pk)
    if not queryset:
        # if there's no cache for this category, get it from the database
        channels = Category.objects.get(pk=pk).channels.all()
        queryset = Video.objects.filter(channel__in=channels).exclude(m3u8=None).order_by('?')
        # Set cache for use later.
        cache.set('random_category_'+pk, queryset, 3600)

    # apply geo block
    if request.GET.get('geo_block'):
        queryset = queryset.filter(channel__geo_protected=False)

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
                                 "lang": request.GET.get('lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
