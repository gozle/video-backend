import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import Client, TariffSubscription


@api_view(['GET'])
@csrf_exempt
def activate_plan(request):
    # Get the verification code from the request
    verification_code = request.GET.get('code')
    subscription_id = request.GET.get('subscription_id')

    # Get the client_id and client_secret
    client_id = Client.objects.all().first().client_id
    client_secret = Client.objects.all().first().client_secret

    payment_url = "https://i.gozle.com.tm/api/payment/perform"
    # Make the request to the verification endpoint
    data = {"verification_code": verification_code, "client_id": client_id, "client_secret": client_secret}
    response = requests.post(payment_url, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        user_id = response.json().get('user_id')
        if request.user.user_id == user_id:
            subscription = TariffSubscription.objects.get(id=subscription_id)
            subscription.activate()
            return Response({"message": "Subscription activated"})
        else:
            return Response({"User's not same"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
