from django.views.decorators.csrf import csrf_exempt

from files.models import Video, Category
from files.serializers import VideoSerializer, CategorySerializer
from files.documents import VideoDocument

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from elasticsearch_dsl import Q


class VideoApi(ListAPIView):
    queryset = Video.objects.exclude(m3u8='').exclude(m3u8=None)
    serializer_class = VideoSerializer

    def get(self, request, **kwargs):
        queryset = self.get_queryset()

        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get(
            'offset') if request.GET.get('offset') else 10
        result_page = paginator.paginate_queryset(
            queryset=queryset, request=request)
        serializer = VideoSerializer(result_page, many=True, context={
            "lang": request.GET.get('lang')})

        return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def get_video(request, pk):
    video = Video.objects.get(pk=pk)

    video.view = video.view + 1
    video.save()

    serializer = VideoSerializer(
        video, context={"lang": request.GET.get('lang')})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def search_video(request):
    q = request.GET.get('q')

     # Get pagination data from request
    page_size = int(request.GET.get('amount', 10))

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
    if not videos.exists():
        return Response({})
    paginator.page_size = page_size

    # Paginate result
    result_page = paginator.paginate_queryset(queryset=videos, request=request)

    serializer = VideoSerializer(result_page, many=True, context={
        "lang": request.GET.get('lang'), 'remove_fields': ['category']})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def search_video_web(request):
    """
        View function for search video from web.
        """
    # Get pagination data from request
    page_size = int(request.GET.get('amount', 10))

    # Get the query string from
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
    if not videos.exists():
        return Response({})
    paginator.page_size = page_size

    # Paginate result
    result_page = paginator.paginate_queryset(queryset=videos, request=request)

    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get('lang')})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def get_videos_by_category(request):
    pk = request.GET.get('pk')

    queryset = Category.objects.get(pk=pk).videos.exclude(m3u8=None).order_by('?')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
        "lang": request.GET.get('lang')})
    return Response(serializer.data)


### CATEGORY API    ####
@api_view(('GET',))
def category_api(request):
    """
    View function to get all categories.
    """
    lang = request.GET.get('lang')
    categories = Category.objects.all()

    serializer = CategorySerializer(categories, many=True, context={"lang": lang})
    return Response(serializer.data)
