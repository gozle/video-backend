from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from files.models import Video
from files.serializers import VideoSerializer


class VideoApi(ListAPIView):
    # Define queryset and serializer class
    queryset = Video.objects.exclude(m3u8='')
    serializer_class = VideoSerializer

    def get(self, request):
        # apply geo block
        if request.GET.get('geo_block'):
            return HttpResponse()

        # Config pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get('offset') if request.GET.get('offset') else 10

        queryset = self.get_queryset()

        # Paginate and serialize queryset
        result_page = paginator.paginate_queryset(queryset=queryset, request=request)
        serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get('lang')})

        return Response(serializer.data)
