from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from files.models import Category
from files.serializers import CategorySerializer



@api_view(('GET',))
def category_api(request):
    # apply geo block
    if request.GET.get('geo_block'):
        return HttpResponse()
    """
    View function to get all categories.
    """
    lang = request.GET.get('lang')
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True, context={"lang": lang})
    return Response(serializer.data)
