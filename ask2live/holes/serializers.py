from rest_framework import serializers
from holes.models import Hole, LiveHole

class HoleSerializer(serializers.ModelSerializer):

    # username = serializers.SerializerMethodField('get_username_from_author')

    class Meta:
        model = Hole
        fields = '__all__'
    

class LiveHoleSerializer(serializers.ModelSerializer):
    # hole = serializers.PrimaryKeyRelatedField(many=False, queryset=Hole.objects.all())
    class Meta:
        model = LiveHole
        # 모델에 있는 컬럼 중에 선택
        fields = ['host_uid', 'room_number', 'audience_list', 'hole'] 
        # fields = '__all__'
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