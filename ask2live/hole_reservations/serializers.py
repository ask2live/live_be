from rest_framework import serializers
from . import models

class HoleReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Reservation
        fields = ['target_demand', 'reserve_start_date', 'finish_date','hole',]
        # fields = '__all__'