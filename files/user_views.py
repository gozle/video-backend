from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from files.models import Comment, Channel, Video, Ad, Category, Playlist, Like, VideoView
from users.models import Keyword
from files.serializers import CommentSerializer, KeywordSerializer, VideoSerializer, ChannelSerializer, \
    CombinedSerializer, PlaylistSerializer, CategorySerializer
from files.documents import VideoDocument, ChannelDocument

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from elasticsearch_dsl import Q
from datetime import datetime, timedelta


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@api_view(('GET',))
@csrf_exempt
def subscribers(request):
    channel_id = request.GET.get('channel_id')
    action = request.GET.get('action')
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    if channel_id:
        try:
            channel = Channel.objects.get(id=channel_id)
            if user not in channel.subscribers.all():
                channel.subscribers.add(user)
            if action == 'unsubscribe':
                if user in channel.subscribers.all():
                    channel.subscribers.remove(user)
        except:
            pass
    channels = user.subscriptions.all()
    return Response(ChannelSerializer(channels, many=True, context={'user': user}).data)


@api_view(('GET',))
@csrf_exempt
def history(request):
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    if request.GET.get('action') and request.GET.get('action') == 'remove' and request.GET.get('pk'):
        video = Video.objects.get(pk=request.GET.get('pk'))
        user.user_views.remove(video)

    queryset = user.user_views.all().order_by('videoview')
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
def comments(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    video = Video.objects.get(pk=request.GET.get('video_id'))
    comments = video.comments.all()

    filter = request.GET.get('filter')
    order = request.GET.get('order')

    filter = {'date': 'created_at', 'random': '?'}[
        filter] if filter else 'date'
    order = {'asc': '', 'desc': '-'}[order] if order else '-'
    comments = comments.order_by(order + filter)

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get(
        'offset') if request.GET.get('offset') else 10
    result_page = paginator.paginate_queryset(
        queryset=comments, request=request)
    serializer = CommentSerializer(result_page, many=True)

    return Response(serializer.data)


@api_view(('POST',))
@csrf_exempt
def add_comment(request):
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    video = Video.objects.get(pk=request.POST.get('video_id'))
    text = request.POST.get('text')

    comment = Comment.objects.create(user=user, video=video, text=text)
    comment.save()

    serializer = CommentSerializer(comment)

    return Response(serializer.data)


@api_view(["POST", "DELETE"])
@csrf_exempt
def like_video(request):
    try:
        video = Video.objects.get(pk=request.data.get('video_id'))
    except ObjectDoesNotExist:
        return Response({"message": "Video not found"}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        user = request.user
        if not Like.objects.filter(user=user, video=video).exists():
            like = Like.objects.create(user=user, video=video)
            like.save()
            return Response({"message": "User liked this video!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User liked this video already!"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user = request.user
        if Like.objects.filter(user=user, video=video).exists():
            Like.objects.filter(user=user, video=video).delete()
            return Response({"message": "User removed like!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User didn't like this video!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
@csrf_exempt
def keywords(request):
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    if request.GET.get('action') and request.GET.get('action') == 'remove' and request.GET.get('keyword'):
        keyword = Keyword.objects.get(keyword=request.GET.get('keyword'))
        user.keyword_history.remove(keyword)

    queryset = user.keyword_history.all()
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get(
        'offset') if request.GET.get('offset') else 10
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = KeywordSerializer(result_page, many=True)

    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def ignored(request):
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    if request.GET.get('action') and request.GET.get('action') == 'add' and request.GET.get('pk'):
        video = Video.objects.get(pk=request.GET.get('pk'))
        video.ignore_users.add(user)

    if request.GET.get('action') and request.GET.get('action') == 'remove' and request.GET.get('pk'):
        video = Video.objects.get(pk=request.GET.get('pk'))
        video.ignore_users.remove(user)

    queryset = user.ignored_videos.all()
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get(
        'offset') if request.GET.get('offset') else 10
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True)

    return Response(serializer.data)


"""     USER END    """

"""     VIDEO     """


class VideoApi(ListAPIView):
    queryset = Video.objects.exclude(m3u8='').exclude(m3u8=None)
    serializer_class = VideoSerializer

    def get(self, request, **kwargs):
        user = None
        if not request.user.is_anonymous:
            user = request.user

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
    user = None
    if not request.user.is_anonymous:
        user = request.user

    video = Video.objects.get(pk=pk)

    video.view = video.view + 1
    video.save()

    if user:
        if VideoView.objects.filter(user=user, video=video).exists():
            VideoView.objects.filter(user=user, video=video).delete()

        view = VideoView(user=user, video=video)
        view.save()

    serializer = VideoSerializer(
        video, context={"lang": request.GET.get('lang'), 'user': user})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def search_video(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    q = request.GET.get('q')

    if user:
        if not Keyword.objects.filter(keyword=q):
            Keyword.objects.create(keyword=q)
        user.keyword_history.add(Keyword.objects.get(keyword=q))

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
def get_channel_video(request, pk):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    sort = request.GET.get('sort')
    sort = {'view': 'view', 'date': 'published_at', 'random': 'random'}[sort]
    order = request.GET.get('order')
    order = {'asc': '', 'desc': '-'}[order]
    object = Channel.objects.get(pk=pk)
    object.view += 1
    object.save()
    if sort == 'random':
        videos = object.videos.exclude(
            m3u8='').exclude(m3u8=None).order_by('?')
    else:
        videos = object.videos.exclude(m3u8='').exclude(
            m3u8=None).order_by(order + sort)

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(queryset=videos, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
        "lang": request.GET.get('lang')})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def get_videos_by_category(request):
    pk = request.GET.get('pk')
    queryset = cache.get('random_category_' + pk)
    if not queryset:
        channels = Category.objects.get(
            pk=pk).channels.all()
        queryset = Video.objects.filter(
            channel__in=channels).exclude(m3u8='').exclude(m3u8=None).order_by('?')
        cache.set('random_category_' + pk, queryset, 3600)

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={
        "lang": request.GET.get('lang')})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def popular_videos(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    time = int(request.GET.get('time'))
    ago = datetime.now() - timedelta(time)
    queryset = Video.objects.exclude(m3u8='').exclude(m3u8=None).filter(
        date__gte=ago).order_by('-view')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)

    if request.GET.get('mob'):
        ad = Ad.objects.filter(category='home', is_active=True).order_by('?')
        if ad.exists():
            ad = ad[0]
            serializer = CombinedSerializer({'video_data': result_page, 'ad_data': ad},
                                            context={"lang": request.GET.get(
                                                'lang'), 'mobile': 'True',
                                                'remove_fields': ['category', 'description']})
            return Response(serializer.data['data'])
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category', 'description']})
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def latest_videos(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    queryset = Video.objects.exclude(
        m3u8='').exclude(m3u8=None).order_by('-published_at')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = VideoSerializer(result_page, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category', 'description'], "user": user})
    return Response(serializer.data)


"""    VIDEO  END   """

"""     CHANNELS    """


@api_view(('GET',))
@csrf_exempt
def channels(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    if request.GET.get('query'):
        query = request.GET.get('query')

        if user:
            if not Keyword.objects.filter(keyword=query):
                Keyword.objects.create(keyword=query)
            user.keyword_history.add(Keyword.objects.get(keyword=query))

        search_document = ChannelDocument()
        query = Q('multi_match', query=query, fields=[
            'name', 'description', 'keywords'], fuzziness='auto')
        search = search_document.search().query(query)
        objects = search.execute()
        ids = [obj.id for obj in objects]
        queryset = Channel.objects.filter(id__in=ids)
    else:
        queryset = Channel.objects.all().order_by('-view')

    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('amount')
    result_page = paginator.paginate_queryset(
        queryset=queryset, request=request)
    serializer = ChannelSerializer(result_page, many=True)
    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def channel(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    queryset = Channel.objects.get(pk=request.GET.get('pk'))
    serializer = ChannelSerializer(queryset, context={"user": user})
    return Response(serializer.data)


"""     CHANNEL  END     """


@api_view(('GET',))
@csrf_exempt
def playlists(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    channel = request.GET.get('channel')
    amount = request.GET.get('amount')
    filter = request.GET.get('filter')
    order = request.GET.get('order')

    # ADD SEARCH

    if request.GET.get('id'):
        playlist = Playlist.objects.get(id=request.GET.get('id'))
        playlist.view += 1
        playlist.save()
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)

    objects = Playlist.objects.all()

    if channel:
        objects = objects.filter(channel_id=channel)

    filter = {'popular': 'view', 'latest': 'created_at', 'random': '?'}[
        filter] if filter else 'created_at'
    order = {'asc': '', 'desc': '-'}[order] if order else '-'
    objects = objects.order_by(order + filter)

    paginator = PageNumberPagination()
    paginator.page_size = amount if amount else 10

    result = paginator.paginate_queryset(queryset=objects, request=request)
    serializer = PlaylistSerializer(result, many=True, context={
        'remove_fields': ['videos']})

    return Response(serializer.data)


@api_view(('GET',))
@csrf_exempt
def shorts_api(request):
    user = None
    if not request.user.is_anonymous:
        user = request.user

    channel = request.GET.get('channel')
    category = request.GET.get('category')
    amount = request.GET.get('amount')
    filter = request.GET.get('filter')
    order = request.GET.get('order')

    # ADD SEARCH

    if request.GET.get('id'):
        shorts = Video.objects.get(id=request.GET.get('id'))
        shorts.view += 1
        shorts.save()
        serializer = VideoSerializer(shorts)
        return Response(serializer.data)

    objects = Video.objects.filter(
        type='shorts').exclude(m3u8=None).exclude(m3u8='')

    if channel:
        objects = objects.filter(channel_id=channel)

    if category:
        objects = objects.filter(category=Category.objects.get(id=category))

    filter = {'popular': 'view', 'latest': 'date', 'random': '?'}[
        filter] if filter else 'date'
    order = {'asc': '', 'desc': '-'}[order] if order else '-'
    objects = objects.order_by(order + filter)

    paginator = PageNumberPagination()
    paginator.page_size = amount if amount else 10

    result = paginator.paginate_queryset(queryset=objects, request=request)
    serializer = VideoSerializer(result, many=True, context={"lang": request.GET.get(
        'lang'), 'remove_fields': ['category', 'description']})

    return Response(serializer.data)


### CATEGORY API    ####
@cache_page(CACHE_TTL*4*24*15)
@api_view(('GET',))
def category_api(request):
    """
    View function to get all categories.
    """
    lang = request.GET.get('lang')
    categories = Category.objects.all()

    serializer = CategorySerializer(categories, many=True, context={"lang": lang})
    return Response(serializer.data)
