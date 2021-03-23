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
    class Meta:
        model = models.User
        fields = ['pk','email', 'work_field','login_method','rating','hole_open_auth' ]

