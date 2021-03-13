from rest_framework import serializers
from . import models 


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type':'password'}, write_only= True)    
    class Meta:
        model = models.User
        fields = ['email', 'password', 'password2','work_field']
        extra_kwargs = {
            'password' : {'write_only': True} # for security
        }
    def save(self):
        account = models.User(
            email = self.validated_data['email'],
            # username=self.validated_data['username'],
            work_field = self.validated_data['work_field']
        )
        password= self.validated_data['password']
        password2= self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account
    

class ReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['email', 'work_field',]
