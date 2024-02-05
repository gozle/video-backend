import base64
import hashlib
import random
import string

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import Client


@api_view(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def get_client(request):
    client = Client.objects.all().first()

    code_verifier = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(43, 128)))
    code_verifier = base64.urlsafe_b64encode(code_verifier.encode('utf-8'))

    code_challenge = hashlib.sha256(code_verifier).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').replace('=', '')

    return Response({"client_id": client.client_id, "callback_uri": client.callback_uri,
                     "login_uri": client.login_uri, "code_challenge": code_challenge, "code_verifier": code_verifier})
