from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Category
from files.serializers import CategorySerializer

CACHE_TTL = settings.CACHE_TTL


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
