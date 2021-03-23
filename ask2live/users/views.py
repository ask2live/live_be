from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view,authentication_classes, permission_classes

from . import models
from .serializers import RegistrationSerializer,UserPropertiesSerializer,ChangePasswordSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView # logout용 API VIEW
from rest_framework.generics import UpdateAPIView

# Create your views here.
@api_view(['POST',])
@permission_classes([]) # 회원 가입할 때는 permission을 따로 적용하지 않기 때문에 빈 값으로.
@authentication_classes([]) #회원 가입 할 때 인증을 따로 적용하지 않기 때문에 빈 값으로.
def registration_view(request):
    if request.method == "POST":
        data={}
        email = request.data.get('email','0').lower()
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
            data['hole_open_auth'] = account.hole_open_auth
            token = Token.objects.get(user=account).key
            print("회원가입 시 token:",token)
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
        email = request.data.get('username')
        password = request.data.get('password')
        print("authenticate 전 account:", email, password)
        account = authenticate(username=email, password=password) #account는 이메일로 나옴. email이 안되서 username으로 키를 바꿔봄
        print("authenticate 한 account:", account)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoestNotExist:
                token = Token.objects.create(user=account)
            print("로그인 시 token:",token)
            context['response'] = 'Successfully login'
            context['pk'] = account.pk
            context['email'] = email.lower()
            context['token'] = token.key
            context['hole_open_auth'] = account.hole_open_auth
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
@permission_classes([IsAuthenticatedOrReadOnly,]) #특정 유저 조회할 때는 허가 필요
# @permission_classes((IsAuthenticated,)) #특정 유저 조회할 때는 허가 필요
def user_properties_view(request):
    try:
        # print("request_user",request)
        account = request.user
        # print("user 정보 보기:",request.user)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        # account = models.User.objects.all()
        # account = models.User.objects.filter(email=account)
        serializer = UserPropertiesSerializer(account)
        # serializer = UserPropertiesSerializer(account,many=True)
        return Response(serializer.data)

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

@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):
	if request.method == 'GET':
		email = request.GET['email'].lower()
		data = {}
		try:
			account = Account.objects.get(email=email)
			data['response'] = email
		except Account.DoesNotExist:
			data['response'] = "Account does not exist"
		return Response(data)



class ChangePasswordView(UpdateAPIView):
	serializer_class = ChangePasswordSerializer
	model = models.User
	permission_classes = []
	authentication_classes = []

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			# Check old password
			if not self.object.check_password(serializer.data.get("old_password")):
				return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

			# confirm the new passwords match
			new_password = serializer.data.get("new_password")
			confirm_new_password = serializer.data.get("confirm_new_password")
			if new_password != confirm_new_password:
				return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

			# set_password also hashes the password that the user will get
			self.object.set_password(serializer.data.get("new_password"))
			self.object.save()
			return Response({"response":"successfully changed password"}, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


