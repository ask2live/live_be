from rest_framework import serializers
from . import models 


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only= True)    
    class Meta:
        model = models.User
        fields = ['email', 'password', 'password2','work_field', 'hole_open_auth','nickname']
        extra_kwargs = {
            'password' : {'write_only': True} # for security
        }
    def save(self):
        account = models.User(
            email = self.validated_data['email'],
            nickname=self.validated_data['nickname'],
            work_field = self.validated_data['work_field'],
            hole_open_auth = self.validated_data['hole_open_auth']
        )
        password= self.validated_data['password']
        password2= self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account


class UserPropertiesSerializer(serializers.ModelSerializer): # 필드 필요하면 추가해야 함.
    class Meta:
        model = models.User
        fields = [
            'pk',
            'email', 
            'work_field',
            'login_method',
            'rating',
            'hole_open_auth',
            'profile_image',
            'nickname', 
            'work_company',
            'bio',
            ]

class AllUserPropertiesSerializer(serializers.ModelSerializer): # 필드 필요하면 추가해야 함.
    class Meta:
        model = models.User
        fields = [
            'id',
            'email', 
            'nickname', 
            'hole_open_auth',
            'work_field',
            'work_company',
            'bio',
            'profile_image',
            'rating',
            'login_method',
            ]


class ChangePasswordSerializer(serializers.Serializer): # 비밀번호 변경용
	old_password 				= serializers.CharField(required=True)
	new_password 				= serializers.CharField(required=True)
	confirm_new_password 		= serializers.CharField(required=True)