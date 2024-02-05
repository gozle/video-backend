from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.documents import ChannelDocument
from files.models import Channel
from files.serializers import VideoSerializer, ChannelSerializer
from elasticsearch_dsl import Q

from files.utils import get_channel_queryset


@cache_page(settings.CACHE_TTL)
@api_view(('GET',))
@csrf_exempt
def channels(request):
    """
    This view function can be used for searching videos of a given channel,
    or for searching channels by query,
    or for getting all channels
    """
    if request.GET.get('id'):
        # If channel id is given, search videos of that channel with a given query.
        query = request.GET.get('query')
        pk = request.GET.get('id')
        queryset = Channel.objects.get(pk=pk).videos.exclude(m3u8='').filter(
            Q(description__icontains=query) | Q(title__icontains=query)).order_by('-pk')
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get('amount')
        result_page = paginator.paginate_queryset(
            queryset=queryset, request=request)
        serializer = VideoSerializer(result_page, many=True)
        return Response(serializer.data)
    elif request.GET.get('query'):
        # If a query given, search channels by given query.
        q = request.GET.get('query')
        search_document = ChannelDocument()
        query = Q('bool',
                  should=[
                      Q('bool', should=[
                          Q('match', **{'name': {'query': q, 'fuzziness': 1, 'boost': 2}}),
                      ]),
                      Q('bool', should=[
                          Q('match', **{'description': {'query': q}}),
                      ]),
                      Q('bool', should=[
                          Q('match', **{'keywords': {'query': q}}),
                      ])
                  ]
                  )
        # Search channels
        search = search_document.search().query(query)
        objects = search.execute()
        ids = [obj.id for obj in objects]
        queryset = get_channel_queryset().filter(id__in=ids)

    else:
        # If any option is not given, select all channels.
        queryset = get_channel_queryset().order_by('-view')

    # apply geo block
    if request.GET.get('geo_block'):
        queryset = queryset.filter(geo_protected=False)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = ChannelSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
