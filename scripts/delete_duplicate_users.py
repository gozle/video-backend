import os
import sys
import django

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()

from django.db.models import Count
from users.models import User


duplicates = User.objects.values('user_id').annotate(count=Count('id')).filter(count__gte=2)
print(len(duplicates))
for duplicate in duplicates:
    value_to_keep = User.objects.filter(user_id=duplicate['user_id']).first()
    User.objects.filter(user_id=duplicate['user_id']).exclude(id=value_to_keep.id)

