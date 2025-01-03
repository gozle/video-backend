from django.urls import path

from files.views import *

urlpatterns = [
    path('api/video', VideoApi.as_view()),
    path('api/banner', banner_api),
    path('api/ad', ad_api),
    path('api/search', searchVideo),
    path('api/web-search', search_video_web),
    path('api/video/<int:pk>', get_video),
    path('api/category', category_api),
    path('api/video-by-category', get_videos_by_category),
    path('api/popular', popular_videos),
    path('api/laters', latest_videos),
    path('api/video-by-channel/<int:pk>', get_videos_of_channel),
    path('api/channels', channels),
    path('api/channel', channel),
    path('api/icons', icons),
    path('api/playlists', playlist_api),
    path('api/shorts', shorts_api),
]
