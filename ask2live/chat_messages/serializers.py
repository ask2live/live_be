from rest_framework import serializers
from chat_messages.models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source ='sender.username', read_only=True)
    class Meta:
        model= Message
        fields= [
            'id',
            'text',
            'sender',
            'sender_username',
            'livehole',
            'sent_timestamp',
            # 'start_at',
        ]
        read_only_fields=['id']
    
    def create(self, validated_data): 
        # validated data로 넘어올 때는 모델에 정의된 필드 혹은 인스턴스로 넘어와야 valid 처리 됨.
        # 예를 들어 datetime의 경우 datetime 타입으로 넘어와야 함.
        print("DEBUG | Message Serializser Create")
        instance = self.Meta.model(**validated_data)
        sender = validated_data['sender']
        instance.sender = sender
        
        text = validated_data['text']
        instance.text = text
        
        livehole = validated_data['livehole']
        instance.livehole = livehole 
        instance.save()
        return instance
