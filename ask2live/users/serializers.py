from rest_framework import serializers
from . import models 


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only= True)    
    class Meta:
        model = models.User
        fields = ['email', 'password', 'password2','work_field', 'hole_open_auth']
        extra_kwargs = {
            'password' : {'write_only': True} # for security
        }
    def save(self):
        account = models.User(
            email = self.validated_data['email'],
            # username=self.validated_data['username'],
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
    # nickname = serializers.CharField(read_only=True) # Charfield는 json으로 주기 위한 타입 설정인가?
    # work_field = serializers.CharField(read_only=True)
    # work_company = serializers.CharField(read_only=True)
    # profile_image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
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
    # def update(self,instance, validated_data):
    #     print("validated _Data", validated_data)
    #     instance = self.Meta.model(**validated_data)
    #     # user = self.context['request'].user
    #     # instance.hole.host = user 

    #     instance.save()
    #     return instance


class ChangePasswordSerializer(serializers.Serializer): # 비밀번호 변경용
	old_password 				= serializers.CharField(required=True)
	new_password 				= serializers.CharField(required=True)
	confirm_new_password 		= serializers.CharField(required=True)