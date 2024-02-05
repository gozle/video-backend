from random import choice

from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Ad
from files.serializers import AdSerializer


@cache_page(10)
@api_view(('GET',))
def ad_api(request):
    """
    This view function returns random ad
    """
    # Get all active ads
    pks = Ad.objects.exclude(category='home').filter(is_active=True).values_list('pk', flat=True)
    if not pks:
        return Response({'message': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    # Select a random ad
    random_pk = choice(pks)
    queryset = Ad.objects.get(pk=random_pk)
    # Increment view counter
    queryset.view += 1
    queryset.save()
    # Serialize and return the ad
    serializer = AdSerializer(queryset, context={'lang': request.GET.get('lang')})
    return Response(serializer.data)
