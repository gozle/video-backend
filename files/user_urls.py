from django.urls import path

from files.user_views import *

urlpatterns = [
    path('video', VideoApi.as_view()),
    path('video/<int:pk>', get_video),
    path('search', search_video),
    path('web-search', search_video_web),
    path('popular', popular_videos),
    path('laters', latest_videos),
    path("category", category_api),

    path('video-by-channel/<int:pk>', get_channel_video),
    path('video-by-category', get_videos_by_category),

    path('channels', channels),
    path('channel', channel),

    path('playlists', playlists),
    path('shorts', shorts_api),

    path('comments', comments),
    path('like', like_video),
    path('add-comment', add_comment),
    path('ignored', ignored),
    path('keywords', keywords),
    path('history', history),
    path('subscribers', subscribers)
]
