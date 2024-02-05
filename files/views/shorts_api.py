from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Video, Category
from files.serializers import VideoSerializer


@api_view(('GET',))
@csrf_exempt
def shorts_api(request):
    # Get data from request
    channel = request.GET.get('channel')
    category = request.GET.get('category')
    amount = request.GET.get('amount')
    filter = request.GET.get('filter')
    order = request.GET.get('order')

    # TODO: Add search logic here

    if request.GET.get('id'):
        # Get shorts by id
        shorts = Video.objects.get(id=request.GET.get('id'))
        shorts.view += 1
        shorts.save()
        serializer = VideoSerializer(shorts)
        return Response(serializer.data)

    # Get all shorts
    objects = Video.objects.filter(
        type='shorts').exclude(m3u8=None).exclude(m3u8='')

    if channel:
        # If a channel is specified, filter by channel
        objects = objects.filter(channel_id=channel)

    if category:
        # If category is specified, filter by category
        objects = objects.filter(category=Category.objects.get(id=category))

    # Reorder queryset with given values
    filter = {'popular': 'view', 'latest': 'date', 'random': '?'}[
        filter] if filter else 'date'
    order = {'asc': '', 'desc': '-'}[order] if order else '-'
    objects = objects.order_by(order+filter)

    # apply geo block
    if request.GET.get('geo_block'):
        objects = objects.filter(channel__geo_protected=False)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = amount if amount else 10

    result = paginator.paginate_queryset(queryset=objects, request=request)
    serializer = VideoSerializer(result, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category', 'description']})

    return Response(serializer.data)

