from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch_dsl import Q
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.documents import VideoDocument
from files.models import Video
from files.serializers import VideoSerializer


@api_view(('GET',))
@csrf_exempt
def searchVideo(request):
    # apply geo block
    if request.GET.get('geo_block'):
        return HttpResponse()

    """
    Search video by keyword
    """
    # Get pagination data from request
    page_size = int(request.GET.get('amount', 10))

    # Get keyword from request
    q = request.GET.get('q')

    # Search from elasticsearch
    search_document = VideoDocument()
    query = Q('bool',
              should=[
                  Q('bool', should=[
                      Q('match', **{'title': {'query': q, 'fuzziness': 1, 'boost': 2}}),
                  ]),
                  Q('bool', should=[
                      Q('match', **{'description': {'query': q}}),
                  ])
              ]
              )
    search = search_document.search().query(query)[:250]
    objects = search.execute()

    # Get videos for result objects
    ids = [obj.id for obj in objects]
    videos = Video.objects.exclude(m3u8=None).exclude(m3u8='').filter(id__in=ids)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    # Paginate result
    result_page = paginator.paginate_queryset(queryset=videos, request=request)

    serializer = VideoSerializer(result_page, many=True, context={
        "lang": request.GET.get('lang'), 'remove_fields': ['category']})
    return paginator.get_paginated_response(serializer.data)
