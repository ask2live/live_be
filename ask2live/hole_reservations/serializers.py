from rest_framework import serializers
from . import models
from datetime import timedelta
class HoleReservationSerializer(serializers.ModelSerializer):
    # hole = serializers.IntegerField(read_only=True, source='hole.id') # 이거를 하니까 model RelatedObjectDoesNotExist 에러가 난다. 커스텀필드를 설정하면 create함수에서 serializer(self)를 통해 들어오고, 이걸 안 하면 validated_data로 들어오는 듯.
    class Meta:
        model = models.Reservation
        fields = [
            'target_demand', 
            'reserve_date', 
            'finish_date',
            'status',
            'guests',
            'hole']
        extra_kwargs = {
            "status": {"required": False, 'read_only': True},
            "guests": {"required": False, "allow_null": True},
            # "hole" : {'read_only': True} 이걸 넣으면 validated_data에 hole이 안들어옴.
            }
    def create(self, validated_data):
        print("validated_data : ", validated_data)
        instance = self.Meta.model(**validated_data) #instance는 __str__ 설정한게 리턴됨. __str__ 안 쓰면 Reservation object (None) 리턴.
        print("instance : ", instance) 
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
        print("validated_data : ", validated_data)
        if validated_data['reserve_date']:
            instance.reserve_date = validated_data['reserve_date']
            instance.finish_date = validated_data['reserve_date'] + timedelta(days=1)
        instance.target_demand = validated_data['target_demand']
        user = self.context['request'].user
        instance.guests.add(user)
        # instance.guests.add(validated_data['guests'])   
        instance.save()
        return instance

# class HoleWishReservationSerializer(serializers.ModelSerializer):
#       class Meta:
#         model = models.Reservation
#         fields = "__all__"
#         extra_kwargs = {
#             # "status": {"required": False, 'read_only': True},
#             "guests": {"required": False, "allow_null": True},
#             # "hole" : {'read_only': True}
#             }
#         def save(self):
#             print("savee")
#             print("self : ", self.instance)
#             user = self.context['request'].user
#             self.instance.guests.add(user)
#             self.instance.save()
#             print("instance guests : ", self.instance.guests)
#             return instance