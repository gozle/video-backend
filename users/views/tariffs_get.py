from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import TariffPlan
from users.serializers import TariffPlanSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tariffs(request):
    plans = TariffPlan.objects.filter(active=True)
    serializer = TariffPlanSerializer(plans, many=True)

    return Response(serializer.data)
