from rest_framework import serializers
from . import models 


class RegistrationSerializer(serializers.ModelSerializer): 
    class Meta:
        model = models.User
        fields = [
            'username', 
            'password', 
            ]
        extra_kwargs = {
            'password' : {'write_only': True} # for security
        }
    def save(self):
        account = models.User(
            username = self.validated_data['username'],
        )
        password= self.validated_data['password']
        account.set_password(password)
        account.save()
        return account


class UserPropertiesSerializer(serializers.ModelSerializer): # 필드 필요하면 추가해야 함.
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    class Meta:
        model = models.User
        fields = [
            'id',
            'username', 
            'work_field',
            'work_company',
            'profile_image',
            'bio',
            'following',
            'followers'
            ]
        read_only_fields = ['following','followers']
        
    def get_following(self, obj):
        follow = FollowingMeSerializer(obj.following.all(), many=True).data
        return follow
        
    def get_followers(self,obj):
        followers = MeFollowersSerializer(obj.followers.all(), many=True).data
        return followers

class FollowingMeSerializer(serializers.ModelSerializer): # 나를 following 하는
    class Meta:
        model= models.UserFollowing
        fields = [
            'id',
            'following_user_id',
            'created'
        ]

class MeFollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFollowing
        fields = [
            'id',
            'user_id',
            'created'
        ]



class ChangePasswordSerializer(serializers.Serializer): # 비밀번호 변경용
	old_password 				= serializers.CharField(required=True)
	new_password 				= serializers.CharField(required=True)
	confirm_new_password 		= serializers.CharField(required=True)