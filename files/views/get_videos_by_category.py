from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from files.models import Category, Video
from files.serializers import VideoSerializer


@api_view(('GET',))
def get_videos_by_category(request):
    # apply geo block
    if request.GET.get('geo_block'):
        return None
    """
    View function to get videos from a specific category
    """
    # Get data from request
    pk = request.GET.get('pk')
    queryset = Category.objects.get(pk=pk).videos.exclude(m3u8=None).order_by('?')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
                                 "lang": request.GET.get('lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
