from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.serializers import UserSerializer


@api_view(['GET'])
@csrf_exempt
def getUserData(request):
    """
    Endpoint for getting user data.
    Args:
        request:
            headers:
                sessionId: The session ID.
    Returns:
        200: User data successfully returned.
        401: Authentication failed.

    """
    if request.user.is_anonymous:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
