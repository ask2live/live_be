import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from chat_messages.models import Message
from holes.models import Hole, LiveHole

from chat_messages.serializers import MessageSerializer
from users.serializers import UserPropertiesSerializer

class ChatConsumer1(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # print("self channel_name : ", self.channel_name,flush=True)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

# -----

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print("self room _name: ",self.scope )
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        room = await self.get_chat_room(self.room_name)
         # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # TODO : cache key에 넣을 room name(group name)을 넘겨준다.
        print("DEBUG | WS Chat connect :: ")
        await self.accept()
        await self.fetch_messages(room)
    
    # leave room group
    async def disconnect(self, close_code):
        print("DEBUG | WS Chat disconnect")
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name)

    
    # receive message from the socket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print("DEBUG | WS Chat receive")
        await self.commands[data['command']](self, data['data'])


    # fetch room messages and send it to the group(룸의 메세지 받아오고 그룹에 send message로 보내기)
    async def fetch_messages(self, room):
        # TODO: cache를 하나 만든다. 키는 방 이름으로 정해서 unique하게 만듬. 
        # cache 키가 있으면, 그걸 바로 group send한다. 아니면 get_serialilzed_message호출
        messages = await self.get_serialized_messages(room)
        print("messages : ", messages)
        # print("fetch_messages")
        # print("room_group_name : ", self.room_group_name)
        await self.channel_layer.group_send(
            self.room_group_name,
                { 
                'type': 'send_message', 
                'message': messages 
                })
    # saves message to db and fetch messages(room으로부터 메세지 받아오고 group에 보내기) again
    async def new_message(self, data):
        # print("new_message data1:", data['sender'])
        # print("new_message data2:", data)
        text = data['text']
        username = data['sender']
        # print("new_message")
        await self.create_room_message(text, username, self.room_name)
        
        # TODO : fetch messages가 아니라 이때부턴 그냥 group send만 하는게 나을듯. (fetch는 처음에 접속할때만 불러오기)
        await self.fetch_messages(self.room_name)

    # receive에서 쓸 커맨드 목록
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }
    # finally send message to the socket
    async def send_message(self, event):
        message = event['message']
        # print("send_message")
        # Send message to WebSocket
        await self.send(text_data=message)
    

    @database_sync_to_async #-> 정확한 의미 알기
    def create_room_message(self, text, username, room):
        author = User.objects.get(username=username) # 이메일 아니면 username으로
        room = LiveHole.objects.get(id=room)
        # print("create_room_message")
        # TODO: cache가 처음에는 없을 테니 roomname 가지고 set을 만들어야 함.
        return Message.objects.create(sender=author, text=text, livehole=room)

    @database_sync_to_async
    def get_serialized_messages(self, room):
        # print("get_serialized_messages room : ", room)
        messages = reversed(Message.objects.filter(livehole=room).order_by('-id')[:20])
        serializer = MessageSerializer(messages, many=True)
        # TODO: cache에도 갱신해야 함.

        # print("get_serialized_messages serializer : ", serializer.data)
        # print("get_serialized_messages")
        return json.dumps(serializer.data)
    
    @database_sync_to_async
    def get_chat_room(self, room):
        # print("get_chat_room | room : ", room)
        return LiveHole.objects.get(id=room) # live hole id말고 channelnum으로 받아오게 하자.
