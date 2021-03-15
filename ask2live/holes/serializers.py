from rest_framework import serializers
from holes.models import Hole

class HoleSerializer(serializers.ModelSerializer):

    # username = serializers.SerializerMethodField('get_username_from_author')

    class Meta:
        model = Hole
        fields = '__all__'
    
    # def get_username_from_author(self, hole):
    #     username = hole.host
    #     return username

