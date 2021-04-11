from rest_framework import serializers
from holes.models import Hole, LiveHole,Participants,Question
from hole_reservations.serializers import HoleReservationSerializer
from datetime import datetime, timedelta
from dateutil.parser import parse

class HoleSerializer(serializers.ModelSerializer):
    host = serializers.CharField(read_only=True, source = 'host.id')
    host_profile_image = serializers.ImageField(source='host.profile_image',max_length=None, use_url=True, allow_null=True, required=False)
    reservation_status = serializers.SlugRelatedField(
        source='hole_reservations',
        slug_field='status',
        read_only=True,
    )
    target_demand = serializers.SlugRelatedField(
        source='hole_reservations',
        slug_field='target_demand',
        read_only=True,
    )
    current_demand = serializers.SlugRelatedField(
        source='hole_reservations',
        slug_field='current_demand',
        read_only=True,
    )
    count_guests = serializers.IntegerField(read_only=True)
    # SlugRelated Field랑 SerializerMethodField 중에 후자는 RelatedObjectDoesNotExist가 나는데 원인 파악 필요
    # reservation_status = serializers.SerializerMethodField(read_only=True, required=False)
    # def get_reservation_status(self, obj):
    #     print("status : ", obj.hole_reservations)
    #     return obj.hole_reservations.status
    class Meta:
        model = Hole
        # fields = '__all__'
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "status",
            "reservation_status",
            "count_guests",
            "target_demand",
            "current_demand",
            "reserve_date",
            "finish_date",
            "host",
            "host_profile_image",
        ]
        extra_kwargs = {
            "status": {"required": False, 'read_only': True},
            # "rating": {"required": False, 'read_only': True},
            "finish_date": {"required": False},
            "reservation_status" : {'read_only':True, "required": False},
            "target_demand" : {'read_only':True, "required": False},
            "current_demand" : {'read_only':True, "required": False},
            }
    def create(self, validated_data): # serializer save 할때 호출됨.
        instance = self.Meta.model(**validated_data)
        finish_date = validated_data['reserve_date'] + timedelta(days=1)
        user = self.context['request'].user
        # user = validated_data['user']
        instance.host = user 
        instance.finish_date = finish_date
        instance.save()
        return instance


class HoleListSerializer(serializers.ModelSerializer):
    host_username = serializers.CharField(source='host.username', read_only=True)
    host_work_field = serializers.CharField(source='host.work_field',read_only=True)
    host_work_company = serializers.CharField(source='host.work_company',read_only=True)
    host_bio = serializers.CharField(source='host.bio',read_only=True)
    host_profile_image = serializers.ImageField(source='host.profile_image',max_length=None, use_url=True, allow_null=True, required=False)
    hole_reservations = HoleReservationSerializer(read_only=True)
    livehole_id = serializers.CharField(source="liveholes.id",read_only=True)
    count_participant = serializers.IntegerField(read_only=True)
    count_questions = serializers.IntegerField(read_only=True)
    class Meta:
        model = Hole
        fields = [
            "id",
            "title",
            "description",
            "reserve_date",
            "finish_date",
            "created",
            "status",
            "host_username",
            "host_work_field",
            "host_work_company",
            "host_bio",
            "host_profile_image",
            "hole_reservations",
            "livehole_id",
            "count_participant",
            "count_questions"
            
        ]
    

class LiveHoleSerializer(serializers.ModelSerializer):
    # hole = serializers.PrimaryKeyRelatedField(many=False, queryset=Hole.objects.all())
    host = serializers.CharField(read_only=True, source = 'hole.host.id')
    host_username = serializers.CharField(read_only=True, source = 'hole.host.username')
    host_profile_image_url = serializers.CharField(read_only=True, source = 'hole.host.profile_image')
    class Meta:
        model = LiveHole
        # 모델에 있는 컬럼 중에 선택
        fields = ['id', 'host_uid', 'audience_uids', 'hole','host','host_username', 'host_profile_image_url'] 
        
    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        user = self.context['request'].user
        instance.hole.host = user 

        instance.save()
        return instance
    # def save(self):
    #     print("vali data: ", self.validated_data)
    #     livehole = LiveHole(
    #         host_uid = self.validated_data['host_uid'],
    #         room_number = self.validated_data['room_number']
    #     )
    #     print("livehole save 전")
    #     print("livehole:",livehole)
    #     livehole.save()
    #     return livehole

class ParticipantSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.ImageField(source='user.profile_image',max_length=None, use_url=True, allow_null=True, required=False)
    username = serializers.CharField(source='user.username',read_only=True)
    work_field = serializers.CharField(source='user.work_field', read_only=True)
    work_company = serializers.CharField(source='user.work_company', read_only=True)
    class Meta:
        model = Participants
        fields = [
          'id', 
          'livehole', 
          'user',
          'profile_image_url',
          'username',
          'work_field',
          'work_company',
          'joined',
          'leaved'
        ]
        read_only_fields = ['id']

class QuestionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True, source='user.id')
    user_username = serializers.CharField(read_only=True, source='user.username')
    user_uid = serializers.IntegerField(read_only=True, source='user.uid')
    user_profile_image_url = serializers.ImageField(source='user.profile_image',max_length=None, use_url=True, allow_null=True, required=False)
    hole = serializers.CharField(read_only=True, source='hole.id')
    class Meta:
        model= Question
        fields = [
            "id",
            "user",
            "user_uid",
            "user_username",
            "user_profile_image_url",
            "hole",
            "question",
            "is_voice",
            "is_answered",
        ]
    def create(self, validated_data): # serializer save 할때 호출됨.
        instance = self.Meta.model(**validated_data) # validated_data에 pk도 들어옴.
        # instance에는 Question 모델 object가 담김.
        user = self.context['request'].user
        hole = Hole.objects.get(id=validated_data['hole'].id)
        # hole = validated_data['pk']
        instance.user = user 
        instance.hole = hole
        instance.save()
        return instance