from django.urls import path

from files.views import *

urlpatterns = [
    path('api/video', VideoApi.as_view()),
    path('api/search', searchVideo),
    path('api/video/<int:pk>', get_video),
    path('api/category', category_api),
    path('api/video-by-category', get_videos_by_category),
    path('api/popular', popular_videos),
    path('api/laters', latest_videos),

]
