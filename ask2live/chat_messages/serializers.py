from rest_framework import serializers
from chat_messages.models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.Charfield(read_only=True, source ='sender.email') # 추후에는 email 대신 username으로 바꿔야 할듯.

    class Meta:
        model= Message
        fields= [
            'id',
            'text',
            'sender',
            'livehole',
            'sent_timestamp',

        ]
        read_only_fields=['id']