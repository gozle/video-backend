from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Ad
from files.serializers import AdSerializer


@api_view(["GET"])
@csrf_exempt
def banner_api(request):
    ad = Ad.objects.filter(category='home', is_active=True).order_by('?')
    if ad.exists():
        ad = ad.first()
        serializer = AdSerializer(ad, context={"request": request, "lang": request.GET.get('lang')})

        return Response(serializer.data)
    else:
        return Response({"message": "Ad not found"}, status=status.HTTP_404_NOT_FOUND)
