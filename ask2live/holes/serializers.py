from rest_framework import serializers
from holes.models import Hole, LiveHole,Participants
from hole_reservations.serializers import HoleReservationSerializer

class HoleSerializer(serializers.ModelSerializer):
    host = serializers.CharField(read_only=True, source = 'host.id')
    # username = serializers.SerializerMethodField('get_username_from_author')
    class Meta:
        model = Hole
        # fields = '__all__'
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "subtitle",
            "description",
            "status",
            "reserve_date",
            "finish_date",
            "host",
            "rating",
        ]
    def create(self, validated_data): # serializer save 할때 호출됨.
        # print("instance validated_data: ", validated_data)
        instance = self.Meta.model(**validated_data)
        # print("instance : ", instance)
        user = self.context['request'].user
        instance.host = user 
        instance.save()
        return instance

class HoleListSerializer(serializers.ModelSerializer):
    host_nickname = serializers.CharField(source='host.nickname', read_only=True)
    host_work_field = serializers.CharField(source='host.work_field',read_only=True)
    host_work_company = serializers.CharField(source='host.work_company',read_only=True)
    host_profile_image = serializers.ImageField(source='host.profile_image',max_length=None, use_url=True, allow_null=True, required=False)
    # reservation_target_demand = serializers.SlugRelatedField(
    #      source='hole_reservations',
    #     slug_field='target_demand',
    #     many=True,
    #     read_only=True,
    #     )
    # status = serializers.CharField(read_only=True)
    hole_reservations = HoleReservationSerializer(read_only=True,many=True)
    livehole_id = serializers.CharField(source="liveholes.id",read_only=True)
    count_participant = serializers.IntegerField(read_only=True)
    # reservation_target_demand = serializers.SerializerMethodField()
    # def get_reservation_target_demand(self, obj):
    #     return obj.hole_reservations.target_demand
    
    class Meta:
        model = Hole
        fields = [
            "id",
            "title",
            "subtitle",
            "description",
            "reserve_date",
            "finish_date",
            "status",
            "host_nickname",
            "host_work_field",
            "host_work_company",
            "host_profile_image",
            "hole_reservations",
            "livehole_id",
            "count_participant",
        ]
    

class LiveHoleSerializer(serializers.ModelSerializer):
    # hole = serializers.PrimaryKeyRelatedField(many=False, queryset=Hole.objects.all())
    host = serializers.CharField(read_only=True, source = 'hole.host.email')
    class Meta:
        model = LiveHole
        # 모델에 있는 컬럼 중에 선택
        fields = ['id', 'host_uid', 'audience_uids', 'hole','host'] 
        
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
    class Meta:
        model = Participants
        fields = [
          'id', 
          'livehole', 
          'user',
          'joined',
          'leaved'
        ]
        read_only_fields = ['id']