import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from chat_messages.models import Message
from holes.models import Hole, LiveHole

from chat_messages.serializers import MessageSerializer
from users.serializers import UserPropertiesSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'room_%s' % self.room_name
        
        room = await self.get_chat_room(self.room_name)
         # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # print("connect")
        await self.accept()
        await self.fetch_messages(room)
    
    # leave room group
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name)

    # receive에서 쓸 커맨드 목록
     commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }
    
    # receive message from the socket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # print("receive:",data)
        await self.commands[data['command']](self, data['data'])


    # fetch room messages and send it to the group(룸의 메세지 받아오고 그룹에 send message로 보내기)
    async def fetch_messages(self, room):
        messages = await self.get_serialized_messages(room)
        # print("fetch_messages")
        # print("room_group_name : ", self.room_group_name)
        await self.channel_layer.group_send(
            self.room_group_name,{ 
                'type': 'send_message', 
                'message': messages 
                })

    # finally send message to the socket
    async def send_message(self, event):
        message = event['message']
        # print("send_message")
        # Send message to WebSocket
        await self.send(text_data=message)
    
    # saves message to db and fetch messages(room으로부터 메세지 받아오고 group에 보내기) again
    async def new_message(self, data):
        text = data['text']
        username = data['sender']
        # print("new_message")
        await self.create_room_message(text, username, self.room_name)
        await self.fetch_messages(self.room_name)

    @database_sync_to_async #-> 정확한 의미 알기
    def create_room_message(self, text, username, room):
        author = User.objects.get(email=username) # 이메일 아니면 username으로
        room = LiveHole.objects.get(id=room)
        # print("create_room_message")
        return Message.objects.create(sender=author, text=text, livehole=room)

    @database_sync_to_async
    def get_serialized_messages(self, room):
        # print("get_serialized_messages room : ", room)
        messages = Message.objects.filter(livehole=room)
        serializer = MessageSerializer(messages, many=True)
        # print("get_serialized_messages serializer : ", serializer)
        # print("get_serialized_messages")
        return json.dumps(serializer.data)
    
    @database_sync_to_async
    def get_chat_room(self, room):
        # print("get_chat_room")
        # print("get_chat_room | room : ", room)
        return LiveHole.objects.get(id=room)
