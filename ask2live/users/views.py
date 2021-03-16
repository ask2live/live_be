from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,authentication_classes, permission_classes

from . import models
from .serializers import RegistrationSerializer,UserPropertiesSerializer
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView # logout용 API VIEW
# Create your views here.

@api_view(['POST',])
@permission_classes([]) # 회원 가입할 때는 permission을 따로 적용하지 않기 때문에 빈 값으로.
@authentication_classes([]) #회원 가입 할 때 인증을 따로 적용하지 않기 때문에 빈 값으로.
def registration_view(request):
    if request.method == "POST":
        data={}
        email = request.data.get('email','0')
        if validate_email(email) != None:
            data['error_message'] = 'That email is already in use.'
            data['response'] = 'Error'
            return Response(data)

        serializer= RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "registration success."
            data['email'] = account.email
            # data['username'] = account.username
            data['work_field'] = account.work_field
            data['pk'] = account.pk
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            data= serializer.errors
        return Response(data)

def validate_email(email):
    account = None
    try: 
        account = models.User.objects.get(email=email)
    except models.User.DoesNotExist:
        return None
    if account != None:
        return email

class ObtainAuthTokenView(APIView): # login용 View를 추가
    authentication_classes= []
    permission_classes = []

    def post(self,request):
        context = {}
        email = request.POST.get('username')
        password = request.POST.get('password')
        account = authenticate(email=email, password=password) #account는 이메일로 나옴.
        # print("authenticate 한 account:", account)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoestNotExist:
                token = Token.objects.create(user=account)
            context['response'] = 'Successfully login'
            context['pk'] = account.pk
            context['email'] = email
            context['token'] = token.key
        else:
            context['response'] = 'Error occurs'
            context['error_message'] = 'Invalid credentials'
        return Response(context)

class Logout(APIView):
    authentication_classes= []
    permission_classes = []
    def post(self, request, format=None):
        # simply delete the token to force a login
        # print(request.user.auth_token)
        request.user.auth_token.delete()
        data = {}
        data['response'] = 'success'
        return Response(data)

@api_view(['GET',])
@permission_classes((IsAuthenticated,)) #특정 유저 조회할 때는 허가 필요
def user_properties_view(request):
    try:
        account = request.user
        # print("user 정보 보기:",request.user)
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
@permission_classes((IsAuthenticated,)) #특정 유저 수정할 때는 허가 필요
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