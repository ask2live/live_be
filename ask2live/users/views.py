from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models
from .serializers import RegistrationSerializer,UserPropertiesSerializer
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

@api_view(['GET',])
def user_properties_view(request):
    try:
        account = request.user
        print("user 정보 보기:",request.user)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserPropertiesSerializer(account)
        return Response(serializer.data)
# class read_view(APIView):
#     def get(self, request,format=None):
#         queryset = models.User.objects.all()
#         serializer = ReadSerializer(queryset, many=True)
#         return Response(serializer.data)

@api_view(['PUT',])
def user_update_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        return response(status=status.HTTP_404_NOT_FOUND)

    if request.method== 'PUT':
        serializer = UserPropertiesSerializer(account, data=request.data)
        data= {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'Update Success'
            return Response(data=data)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)