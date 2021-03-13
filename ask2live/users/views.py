from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models
from .serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView # logout용 API VIEW
# Create your views here.

@api_view(['POST',])
def registration_view(request):
    if request.method == "POST":
        serializer= RegistrationSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "success"
            data['email'] = account.email
            # data['username'] = account.username
            data['work_field'] = account.work_field
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            data= serializer.errors
        return Response(data)

class Logout(APIView):
    def post(self, request, format=None):
        # simply delete the token to force a login
        # print(request.user.auth_token)
        request.user.auth_token.delete()
        data = {}
        data['response'] = 'success'
        return Response(data)