import json,time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from chat_messages.models import Message
from holes.models import Hole, LiveHole

from chat_messages.serializers import MessageSerializer
from users.serializers import UserPropertiesSerializer
from django_redis import get_redis_connection
from django.core.cache import cache
from datetime import datetime,timezone
from ast import literal_eval

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
    # con = get_redis_connection("default")
    # print("redis: con ", con)
    async def connect(self):
        con = get_redis_connection("default")

        self.room_name = self.scope['url_route']['kwargs']['room_id']
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        
        self.author_group_name = "author:%s" % self.room_name
        self.livehole_group_name = "group:livehole"
        room = await self.get_chat_room(self.room_name, self.livehole_group_name,con) # 인자 넘길 때 redis key도 같이 넘기기

         # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # TODO : cache key에 넣을 room name(group name)을 넘겨준다.
        print("DEBUG | WS Chat connect :: ")
        await self.accept()
        await self.fetch_messages(room,con)
    
    # leave room group
    async def disconnect(self, close_code):
        print("DEBUG | WS Chat disconnect")
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name)

    
    # receive message from the socket
    async def receive(self, text_data):
        con = get_redis_connection("default")
        data = json.loads(text_data)
        print("DEBUG | WS Chat receive")
        await self.commands[data['command']](self, data['data'], con)


    # fetch room messages and send it to the group(룸의 메세지 받아오고 그룹에 send message로 보내기)

    async def fetch_messages(self, room,con): # 여기서 캐시에 있는 데이터를 들고온다?
        messages = await self.get_serialized_messages(room,con)
        print("fetch_messages")
        # TODO: cache를 하나 만든다. 키는 방 이름으로 정해서 unique하게 만듬. 
        # cache 키가 있으면, 그걸 바로 group send한다. 아니면 get_serialilzed_message호출
        await self.channel_layer.group_send(
            self.room_group_name,
                { 
                'type': 'send_message', 
                'message': messages 
                })
        
    # saves message to db and fetch messages(room으로부터 메세지 받아오고 group에 보내기) again
    async def new_message(self, data,con):
       
        self.author_group_name = "author:%s" % self.room_name
        text = data['text']
        username = data['sender']
        print("text, username : ", text, username)
        await self.create_room_message(text, username, self.room_name, self.author_group_name, con)
        # print("username new_message : ", username)
        await self.fetch_messages(self.room_name,con)

    # receive에서 쓸 커맨드 목록
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }
    # finally send message to the socket
    async def send_message(self, event):
        message = event['message']
        # print("send_message")
        # print("send message :  ", message)
        # Send message to WebSocket
        await self.send(text_data=message)
    

    @database_sync_to_async
    def create_room_message(self, text, username, room,author_group, con):
        res = con.hexists(author_group, username) # 캐시에 author들이 있는지 확인 : 있으면 캐시히트
        print("create_room_message res : ", res)
        if res == 1:
            author_id= con.hget(author_group, username).decode("utf-8") # 바로 불러옴. 대신 bytes로 리턴이라 디코딩필요
            # print("cache author : ",author_id)
        else:
            author_id = User.objects.get(username=username).id # 메세지 record를 만들기 위해 id로 가지고오기
            # print("db author : ",author_id)
            con.hset(author_group,username,author_id) # 처음 이후부터는 바로 캐시에서 불러오기 위해서 캐시에 추가

        livehole_group = "group:livehole"
        res_livehole = con.hexists(livehole_group, room) # 캐시 livehole group에 해당 livehole num이 있는지 확인
        if res_livehole == 1:
            print("create messages hexists 통과")
            livehole = con.hget(livehole_group,room).decode("utf-8")
            print("livehole : ", livehole)
            # 메세지 오브젝트를 캐시에 넣기 위해 만들기
        else:
            print(" create message live hole db 조회")
            livehole = LiveHole.objects.get(id=room).id
            # 라이브 홀의 경우 id를 바로 알고 있으니까 캐시에 추가할 필요는 없음.
        
        group_key = "message:%s" % livehole
        # print("create_room_message 에서 group_key : ",group_key)
        now_time = datetime.now()

        # 캐시에 저장할 메세지 오브젝트 만들기
        message = {
            "sender" : username,
            "text" : text,
            "livehole" : livehole,
            "sent_timestamp" : now_time
        }
 
        # DB에 넣기 위해 sender를 id로 잠시 변경
        message['sender'] = int(author_id)
        message_serializer = MessageSerializer(data = message)
        if message_serializer.is_valid():
            message_serializer.save()
        # message = Message.objects.create(sender=author_id, text=text, livehole=livehole)
        
        # 메세지 넣는건 캐시에 메세지 데이터 추가하는 것과 별개로 디비에는 담아야 할듯. if else로 나눠서 처리되면 안됨.
        # 메세지 capacity 확인 후 eviction 및 캐시에 넣기
        group_messages_count = con.zcard(group_key)
        if group_messages_count == 20:
            ress = con.zpopmin(group_key)
            # print("ress : ", ress)

        # 새로운 메세지를 sorted set에 넣기
        message['id'] = message_serializer.data['id']
        message['sent_timestamp'] = str(now_time)
        message['sender'] = username
        dict = {}
        dict[str(message)] = time.time()
        con.zadd(group_key, dict)
        cache.expire(group_key, timeout=600)
        # print("con zadd 잘됨!! 메세지 캐시에 담음.")

        return message

    @database_sync_to_async
    def get_serialized_messages(self, room, con):
        # 캐시에 있는 메세지를 가지고오기
        group_key = "message:%s" % room
        # print("get_serialized_messages에서 group_key : ", group_key)
        # print("여기서 캐시는?", cache)
        res = con.exists(group_key)
        # print("res : ", res)
        if res == 1:
            # messages = cache.get(group_key)
            messages = con.zrange(group_key, 0,-1) # 현재 group에 있는 메세지 전부 가져오기
            # print("message : ", messages)
            message_array = []
            for m in messages: # bytes list로 리턴된 걸 디코드하기
                m = m.decode('utf-8')
                # print("디코드 한 m : ", m)
                # print("m의 type : ", type(m))
                # json_acceptable_string = m.replace("'", "\"")
                # print("json_acceptable_string이란 : ", json_acceptable_string)
                # m = json.loads(json_acceptable_string)
                m = literal_eval(m) # string dict를 dict로 만들기

                message_array.append(m)
            #     m = literal_eval(str(m.decode('utf-8')))
            #     # m['text'].decode('utf-8')
            #     message_array.append(m)
            # message_array = [ literal_eval(str(m.decode('utf-8'))) for m in messages]
            # print("messages array : ", message_array)
            # print("get_serialized_messages 캐시쪽으로 들어옴 ")
            
            # dict가 담긴 array를 json array 형태로 저장.
            return json.dumps(message_array)
        else:
            # db에서 메세지를 가지고오기
            messages = Message.objects.filter(livehole=room)
            serializer = MessageSerializer(messages, many=True)
            # print("get_serialized_messages 디비쪽으로 들어옴 ")
            return json.dumps(serializer.data)
    
    @database_sync_to_async
    def get_chat_room(self, room, group,con):
        res = con.hexists(group, room) # live hole을 캐시에서 가져올 수 있는지 확인
        # print("res : ", res)
        # print("get_chat_room에서 room : ", room)
        if res == 1:
            print("hexists 통과")
            livehole = con.hget(group,room).decode("utf-8") # channel num 불러오기
            # print("hash cache get한 livehole : ", livehole)
            # print("hash cache get한 livehole 타입 : ", type(livehole))
        else:
            livehole_qs = LiveHole.objects.get(id=room)
            livehole = livehole_qs.id
            livehole_h = con.hset(group,livehole,livehole)
            # print("hash cache set한 livehole : ", livehole_h)
        return livehole