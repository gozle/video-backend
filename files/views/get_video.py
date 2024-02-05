from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Video
from files.serializers import VideoSerializer


@api_view(('GET',))
@csrf_exempt
def get_video(request, pk):
    # apply geo block
    if request.GET.get('geo_block'):
        return HttpResponse()
    """
    View function for getting video details.
    Args:
        request: Request object.
        pk: ID of the video.

    Returns:
        video: Video details.
    """
    video = Video.objects.get(pk=pk)

    video.view = video.view+1
    video.save()
    video = Video.objects.get(pk=pk)
    serializer = VideoSerializer(video, context={"lang": request.GET.get('lang')})
    return Response(serializer.data)
