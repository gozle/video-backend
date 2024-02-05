import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from users.models import TariffPlan, TariffSubscription, Client
from users.serializers import TariffPlanSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_plan(request):
    # Get data from the request
    user = request.user
    plan_id = request.data.get('tariff_id')

    # Check if the plan exists
    try:
        plan = TariffPlan.objects.get(id=plan_id)
    except ObjectDoesNotExist:
        return Response({"message": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    # Create the subscription
    subscription = TariffSubscription.objects.create(user=user, plan=plan)
    subscription.save()

    # Get the client
    client = Client.objects.all().first()

    # Register payment at OAuth 2.0 server
    oauth_payment_url = "https://i.gozle.com.tm/api/payment/register"
    data = {"user_id": user.user_id,
            "client_id": client.client_id,
            "amount": subscription.plan.price,
            "description": subscription.plan.description}
    response = requests.post(oauth_payment_url, data=data)

    # Check if the payment registration was successful
    if response.status_code == 201:
        return Response({"payment_id": response.json()['payment_id'], "subscription_id": subscription.id})
    else:
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
