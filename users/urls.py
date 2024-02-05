from django.urls import path

from users.views import loginUser, getUserData, get_tariffs, register_plan, activate_plan, get_client

urlpatterns = [
    path('login', loginUser),
    path('get-user', getUserData),
    path('get-client', get_client),
    path('tariff/get', get_tariffs),
    path('tariff/register', register_plan),
    path('tariff/activate', activate_plan),
]
