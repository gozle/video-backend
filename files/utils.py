from django.db.models import Count, Q

from files.models import Channel


def get_channel_queryset():
    return Channel.objects.annotate(video_count=Count("videos", exclude=Q(videos__m3u8=None))).filter(video_count__gt=1)
