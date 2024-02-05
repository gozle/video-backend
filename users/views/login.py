from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
from django.contrib.auth import login
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import Client, User


# TODO: Change this GET request to a POST request on deployment server.
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def loginUser(request):
    """
    Endpoint for logging in a user with OAuth2.0.
    Args:
        request:
            code: The authorization code.
            code_verifier: The code verifier.

    Returns:
        200: User successfully logged in.
        400: Error logging in.

    """
    code = request.data.get('code')
    code_verifier = request.data.get('code_verifier')
    # grant_type = request.POST.get('grant_type')

    grant_type = 'authorization_code'

    client = Client.objects.all().first()
    client_id = client.client_id
    client_secret = client.client_secret
    token_uri = client.token_uri
    resource_uri = client.resource_uri
    redirect_uri = request.data.get("redirect_uri", client.callback_uri)

    headers = {"Cache-Control": "no-cache"}

    data = {"client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            "grant_type": grant_type}

    response = requests.post(
        token_uri, headers=headers, data=data)
    if response.status_code == 200:
        # Successfully got access token and refresh token
        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']

        headers = {"Authorization": "Bearer {}".format(access_token), }

        resource_response = requests.get(resource_uri, headers=headers)
        if resource_response.status_code == 200:
            # Successfully got user data
            user_data = resource_response.json()
            if User.objects.filter(user_id=user_data['id']).exists():
                # User already exists
                user = User.objects.get(user_id=user_data['id'])
                user.access_token = access_token
                user.refresh_token = refresh_token
                user.save()
                login(request, user)
                return Response({"message": "Successfully logged in"}, status=status.HTTP_200_OK)

            if User.objects.filter(username=user_data['username']).exists():
                user = User.objects.get(username=user_data['username'])
                user.delete()

            # Create new user
            user_id = user_data['id']
            username = user_data['username']
            first_name = user_data['first_name']
            last_name = user_data['last_name']
            email = user_data['email']
            phone_number = user_data['phone_number']
            avatar_url = user_data['avatar']
            updated_at = user_data['updated_at']

            avatar_temp = NamedTemporaryFile()
            avatar_temp.write(urlopen(avatar_url).read())
            avatar_temp.flush()

            user = User.objects.create(username=username,
                                       user_id=user_id,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       phone_number=phone_number,
                                       access_token=access_token,
                                       refresh_token=refresh_token,
                                       updated_at=updated_at)
            user.save()
            user.avatar.save(str(user.id) + '.png', File(avatar_temp))
            login(request, user)
            return Response({"message": "Successfully logged in"}, status=status.HTTP_200_OK)
        else:
            # Cannot get user data
            return Response(resource_response.json(), status=status.HTTP_400_BAD_REQUEST)
    else:
        # Cannot get access token
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
