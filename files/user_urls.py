from django.urls import path

from files.user_views import *

urlpatterns = [
    path('video', VideoApi.as_view()),
    path('video/<int:pk>', get_video),
    path('search', search_video),
    path('web-search', search_video_web),
    path("category", category_api),

    path('video-by-category', get_videos_by_category),

]
