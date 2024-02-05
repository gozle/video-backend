import os
import sys
import django

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()

from django.db.models import Count
from files.models import Video


duplicates = Video.objects.values('video_id').annotate(count=Count('id')).filter(count__gte=2)
print(len(duplicates))
for duplicate in duplicates:
    value_to_keep = Video.objects.filter(video_id=duplicate['video_id']).first()
    Video.objects.filter(video_id=duplicate['video_id']).exclude(id=value_to_keep.id).delete()

