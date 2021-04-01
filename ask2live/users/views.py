from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view,authentication_classes, permission_classes

from . import models
from holes.models import Hole
from .serializers import RegistrationSerializer,UserPropertiesSerializer,ChangePasswordSerializer
from holes.serializers import HoleSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView # logout용 API VIEW
from rest_framework.generics import UpdateAPIView
from drf_yasg.utils import swagger_auto_schema

HOST_CRITERIA = 1

# Create your views here.
@swagger_auto_schema(methods=['POST'], request_body=RegistrationSerializer, operation_description="POST /user/register")
@api_view(['POST',])
@permission_classes([]) # 회원 가입할 때는 permission을 따로 적용하지 않기 때문에 빈 값으로.
@authentication_classes([]) #회원 가입 할 때 인증을 따로 적용하지 않기 때문에 빈 값으로.
def registration_or_login_view(request): # 로그인과 회원가입을 동시에 
    if request.method == "POST":
        data={}
        username = request.data.get('username','0').lower()
        password = request.data.get('password')
        if validate_username(username) != None: # 이미 username이 있을 경우 로그인
            account = authenticate(username=username, password=password)
            print("account : ", account)
            if account:
                try:
                    token = Token.objects.get(user=account)
                except Token.DoesNotExist:
                    token = Token.objects.create(user=account)
                data['response'] = 'LOGIN SUCCESS'
                data['detail'] = {}
                data['detail']['token'] = token.key
                return Response(data,status=status.HTTP_200_OK)

        serializer= RegistrationSerializer(data=request.data)

        if serializer.is_valid(): # 아니면 회원가입
            account = serializer.save()
            token = Token.objects.get(user=account).key
            data['response'] = "REGISTER SUCCESS"
            data['detail'] = {}
            data['detail']['pk'] = account.pk
            data['detail']['username'] = account.username
            print("회원가입 시 token:",token)
            data['detail']['token'] = token
            return Response(data,status=status.HTTP_200_OK)
        else:
            data['response'] = "FAIL"
            data['detail'] = "정보가 유효하지 않습니다."
            return Response(data,status=status.HTTP_400_BAD_REQUEST)

def validate_username(username):
    account = None
    try: 
        account = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        return None
    if account != None:
        return username


class Logout(APIView):
    # authentication_classes= []
    permission_classes = [IsAuthenticated,]
    def post(self, request, format=None):
        # simply delete the token to force a login
        print("request : ", request)
        request.user.auth_token.delete()
        data = {}
        data['response'] = 'SUCCESS'
        return Response(data)

@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,]) #특정 유저 조회할 때는 허가 필요
def user_properties_view(request):
    path = request.resolver_match.url_name
    print("path : ", path)
    data = {}
    try:
        # print("request_user",request)
        account = request.user
    except User.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '유저가 없습니다.'
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        if path == "read":
            serializer = UserPropertiesSerializer(account)
            data['response'] = 'SUCCESS'
            data['detail'] = serializer.data
            return Response(data)
        elif path == "read_hole":
            # 본인의 hole 모두 들고오기
            hole = Hole.objects.filter(host=account)
            my_hole_serializer = HoleSerializer(hole, many=True)
            
            # 본인이 guest로 희망하는 hole 들고오기
            wish_user_obj = models.User.objects.get(username=account)
            reservations = wish_user_obj.hole_reservations.filter(guests=account).values_list('hole',flat=True)
            holes = Hole.objects.filter(id__in=reservations) 
            wish_hole_serializer = HoleSerializer(holes,many=True)
            # json에 담아서 보내기
            data['response'] = 'SUCCESS'
            data['detail'] = {}
            data['detail']['my_hole'] = my_hole_serializer.data
            data['detail']['wish_hole'] = wish_hole_serializer.data
            return Response(data)
            

@swagger_auto_schema(methods=['PATCH'], request_body=UserPropertiesSerializer, operation_description="PATCH /user/update")
@api_view(['PATCH',])
@permission_classes((IsAuthenticated,)) #특정 유저 수정할 때는 허가 필요
def user_update_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '유저가 없습니다.'
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    if request.method== 'PATCH':
        data= {}
        user = models.User.objects.get(username=account)
        serializer = UserPropertiesSerializer(user, data=request.data,partial=True)
        print("serializer : ",serializer)
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'SUCCESS'
            return Response(data=data)
        else:
            data['response'] = 'FAIL'
            data['detail'] = '유효한 정보가 아닙니다.'
            return Response(data, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET',])
@permission_classes([]) # 전체 유저 조회
def all_user_properties_view(request):
    data = {}
    if request.method == 'GET':
        account = models.User.objects.all()
        serializer = UserPropertiesSerializer(account, many=True)
        data['response'] = 'SUCCESS'
        data['detail'] = serializer.data
        return Response(data)



@swagger_auto_schema(methods=['POST'], operation_description="POST /user/follow/<user_id>")
@api_view(['POST',])
@permission_classes((IsAuthenticated,)) #특정 유저 수정할 때는 허가 필요
def user_follow_view(request,user_id):
    data= {}
    try:
        user = request.user
    except user.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '유저가 없습니다.'
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    if request.method== 'POST':
        me = models.User.objects.get(username=user)
        following_user = models.User.objects.get(id=user_id)
        models.UserFollowing.objects.create(user_id=me, following_user_id=following_user)
        follow_count = following_user.followers.count()
        # print("follow_count : ", follow_count , HOST_CRITERIA)
        if follow_count == HOST_CRITERIA: #호스트 기준 충족시에만 권한부여
            following_user.hole_open_auth = True
            following_user.save()
        data['response'] = 'SUCCESS'
        return Response(data=data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(methods=['DELETE'], operation_description="DELETE /user/unfollow/<user_id>")
@api_view(['DELETE',])
@permission_classes((IsAuthenticated,)) #특정 유저 수정할 때는 허가 필요
def user_unfollow_view(request,user_id):
    data= {}
    try:
        user = request.user
    except user.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '유저가 없습니다.'
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    if request.method== 'DELETE':
        me = models.User.objects.get(username=user)
        following_user = models.User.objects.get(id=user_id)
        unfollow_user = models.UserFollowing.objects.get(user_id=me, following_user_id=following_user)
        unfollow_user.delete()
        follow_count = following_user.followers.count()
        if follow_count == HOST_CRITERIA-1: #호스트 기준 미충족시에만 권한 취소
            following_user.hole_open_auth = False
            following_user.save()
        data['response'] = 'SUCCESS'
        return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['GET', ])
# @permission_classes([])
# @authentication_classes([])
# def does_account_exist_view(request):
# 	if request.method == 'GET':
# 		username = request.GET['username'].lower()
# 		data = {}
# 		try:
# 			account = Account.objects.get(username=username)
# 			data['response'] = username
# 		except Account.DoesNotExist:
# 			data['response'] = "Account does not exist"
# 		return Response(data)



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


