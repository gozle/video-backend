from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Playlist
from files.serializers import PlaylistSerializer


@api_view(('GET',))
@csrf_exempt
def playlist_api(request):
    """
    Playlist API for all playlist operations.
    """
    # Get data from request
    channel = request.GET.get('channel')
    amount = request.GET.get('amount')
    filter = request.GET.get('filter')
    order = request.GET.get('order')

    # TODO: Add search logic here

    if request.GET.get('id'):
        # If id is provided, get and return the playlist with that id
        playlist = Playlist.objects.get(id=request.GET.get('id'))
        playlist.view += 1
        playlist.save()
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)

    # Get all playlists
    objects = Playlist.objects.all()

    if channel:
        # If a channel is provided, get all playlists with that channel
        objects = objects.filter(channel_id=channel)

    # Reorder queryset with given order and filter
    filter = {'popular': 'view', 'latest': 'created_at', 'random': '?'}[
        filter] if filter else 'created_at'
    order = {'asc': '', 'desc': '-'}[order] if order else '-'
    objects = objects.order_by(order+filter)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = amount if amount else 10

    result = paginator.paginate_queryset(queryset=objects, request=request)
    serializer = PlaylistSerializer(result, many=True, context={'remove_fields': ['videos']})

    return Response(serializer.data)
