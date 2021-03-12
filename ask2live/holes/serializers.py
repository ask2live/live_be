from rest_framework import serializers
from . import models

class HoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hole
        fields = '__all__'

