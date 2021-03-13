from django.urls import path, include
from .views import registration_view, Logout

from rest_framework.authtoken.views import obtain_auth_token
app_name="user"

urlpatterns = [
    path('register', registration_view, name="register"),
    path('login', obtain_auth_token, name="login"),
    path('logout', Logout.as_view(), name="logout")
]

