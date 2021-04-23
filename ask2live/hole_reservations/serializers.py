from rest_framework import serializers
from . import models
from datetime import timedelta
class HoleReservationSerializer(serializers.ModelSerializer):
    # hole = serializers.IntegerField(read_only=True, source='hole.id') # 이거를 하니까 model RelatedObjectDoesNotExist 에러발생. TODO: 명확한 원인 파악 필요 : 커스텀필드를 설정하면 create함수에서 serializer(self)를 통해 들어오고, 이걸 안 하면 validated_data로 들어오는 듯.
    class Meta:
        model = models.Reservation
        fields = [
            'id',
            'target_demand', 
            'reserve_date', 
            'finish_date',
            'status',
            'guests',
            'hole']
        extra_kwargs = {
            "status": {"required": False, 'read_only': True},
            "guests": {"required": False, "allow_null": True},

            }
    def create(self, validated_data):
        print("DEBUG | HoleReservation Serializser Create")
        instance = self.Meta.model(**validated_data) #instance는 __str__ 설정한게 리턴됨. __str__ 안 쓰면 Reservation object (None) 리턴.
        reserve_date = validated_data['reserve_date']
        instance.reserve_start_date = reserve_date
        finish_date = validated_data['finish_date']
        instance.finish_date = finish_date
        target_demand = validated_data['target_demand']

        instance.target_demand = target_demand 
        hole = validated_data['hole']
        instance.hole = hole 
        instance.save()
        return instance
        
    def update(self, instance, validated_data):
        print("DEBUG | HoleReservation Serializser Update")
        if validated_data['reserve_date']:
            instance.reserve_date = validated_data['reserve_date']
            instance.finish_date = validated_data['reserve_date'] + timedelta(days=1)
        if validated_data['target_demand']:
            instance.target_demand = validated_data['target_demand']
        user = self.context['request'].user
        instance.guests.add(user)
        instance.save()
        return instance