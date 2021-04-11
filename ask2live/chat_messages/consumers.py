import json,time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from chat_messages.models import Message
from holes.models import Hole, LiveHole, Question
from holes.serializers import QuestionSerializer

from chat_messages.serializers import MessageSerializer
from users.serializers import UserPropertiesSerializer
from django_redis import get_redis_connection
from django.core.cache import cache
from datetime import datetime,timezone
from ast import literal_eval

class ChatConsumer(AsyncWebsocketConsumer):
    # con = get_redis_connection("default")
    # print("redis: con ", con)
    async def connect(self):
        con = get_redis_connection("default")
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'room_%s' % self.room_name
        
        self.author_group_name = "author:%s" % self.room_name
        self.livehole_group_name = "group:livehole"
        room = await self.get_chat_room(self.room_name, self.livehole_group_name,con) # 인자 넘길 때 redis key도 같이 넘기기
         # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("DEBUG | WS Chat connect :: ")
        await self.accept()
        await self.fetch_messages(room,con)
    
    # leave room group
    async def disconnect(self, close_code):
        print("DEBUG | WS Chat disconnect", close_code)
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name)

    
    # receive message from the socket
    async def receive(self, text_data):
        con = get_redis_connection("default")
        data = json.loads(text_data)
        print("DEBUG | WS Chat receive")
        print("리시브 할 때 data :", data)
        await self.commands[data['command']](self, data['data'], con)


    # fetch room messages and send it to the group(룸의 메세지 받아오고 그룹에 send message로 보내기)
    async def fetch_messages(self, room,con): # 여기서 캐시에 있는 데이터를 들고온다?
        messages = await self.get_serialized_messages(room,con)
        print("fetch_messages")
        # print("room_group_name : ", self.room_group_name)
        await self.channel_layer.group_send(
            self.room_group_name,{ 
                'type': 'init_message', 
                'message': messages 
                })


    # 질문 불러오는 함수
    async def fetch_questions(self, data,con): # 여기서 캐시에 있는 데이터를 들고온다?
        print("complete fetch_questions : ", data)
        question_data = {
            'hole_id' : data['pk']
        }
        questions = await self.get_questions(question_data) # 이걸 만들어야 하나?
        # HttpResponseRedirect로 question all read view 부르면 그거 리턴 받으면 json 나오나? 그거 파싱해서 send 해야할듯.
        print("fetch_questions : ", questions)
        # 질문 리스트 보내는거랑 메세지보내는거랑 type을 나눠야 함.
        await self.channel_layer.group_send(
            self.room_group_name,
                { 
                'type': 'send_questions', 
                'message': questions 
                })

    # 라이브홀 정보 불러오는 함수(participant 조인 시 체크)
    async def fetch_livehole(self, data,con):
        room = await self.get_chat_room(self.room_name, self.livehole_group_name,con)
        print("complete fetch_questions : ", data)
        question_data = {
            'hole_id' : data['pk']
        }
        questions = await self.get_questions(question_data) # 이걸 만들어야 하나?
        # HttpResponseRedirect로 question all read view 부르면 그거 리턴 받으면 json 나오나? 그거 파싱해서 send 해야할듯.
        print("fetch_questions : ", questions)
        # 질문 리스트 보내는거랑 메세지보내는거랑 type을 나눠야 함.
        await self.channel_layer.group_send(
            self.room_group_name,
                { 
                'type': 'send_questions', 
                'message': questions 
                })
    # saves message to db and fetch messages(room으로부터 메세지 받아오고 group에 보내기) again
    async def new_message(self, data,con):
        self.author_group_name = "author:%s" % self.room_name
        print("new message 할 때 : ", data)
        text = data['text']
        username = data['sender']
        print("text, username : ", text, username)
        message = await self.create_room_message(text, username, self.room_name, self.author_group_name, con)
        print("new message에서 message : ", message)
        
        # 4/11 : 메세지 받은걸 바로 broadcast하려고 한다.
        await self.channel_layer.group_send(
            self.room_group_name,
                { 
                'type': 'send_message', 
                'message': message 
                })
        # await self.fetch_messages(self.room_name,con)

    # receive에서 쓸 커맨드 목록
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'fetch_questions' : fetch_questions,
        'fetch_livehole' : fetch_livehole
    }

    # 처음 들어올 때 최근 N개 메세지 보여주기
    async def init_message(self, event):
        print("init_message 에서 event : ", event)
        # event의 type에 따라 분기 처리해서 message 안에 type key를 추가하는식으로 해도 될듯.
        message = event['message']
        print("init_message 에서 message : ", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "ON_MESSAGES_INIT",
            "data": message
        }))


    # finally send message to the socket
    async def send_message(self, event):
        print("send_message 에서 event : ", event)
        # event의 type에 따라 분기 처리해서 message 안에 type key를 추가하는식으로 해도 될듯.
        message = event['message']
        print("send_message 에서 message : ", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "ON_MESSAGES_READ",
            "data": message
        }))

    # 질문을 소켓으로 보내기
    async def send_questions(self, event):
        print("send_questions 에서 event : ", event)
        # event의 type에 따라 분기 처리해서 message 안에 type key를 추가하는식으로 해도 될듯.
        question = event['message']
        print("send_questions 에서 question : ", question)
        # Send message to WebSocket
        # send 할 때 보낼 수 있는 key값이 무엇이 있는지 코드를 까보기
        await self.send(text_data=json.dumps({
            "type": "QUESTION",
            "data": question
        }))
    
    @database_sync_to_async
    def get_questions(self,question_data):
        print("get_questions의 question_data : ", question_data)
        hole = Hole.objects.get(id = question_data['hole_id'])
        questions = Question.objects.filter(hole=hole)
        serializer = QuestionSerializer(questions, many=True)
        return serializer.data


    @database_sync_to_async
    def create_room_message(self, text, username, room,author_group, con):
        print("-----------------create_room_message")
        res = con.hexists(author_group, username) # 캐시에 author들이 있는지 확인 : 있으면 캐시히트
        print("create_room_message res : ", res)
        if res == 1:
            author_id= con.hget(author_group, username).decode("utf-8") # 바로 불러옴. 대신 bytes로 리턴이라 디코딩필요
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

        # 4/11 : 메세지 받은걸 바로 broadcast 하기 위해 json dump해서 보냄.
        return [message]

    @database_sync_to_async
    def get_serialized_messages(self, room, con):
        # 캐시에 있는 메세지를 가지고오기
        group_key = "message:%s" % room
        res = con.exists(group_key)
        if res == 1:
            # messages = cache.get(group_key)
            messages = con.zrange(group_key, 0,-1) # 현재 group에 있는 메세지 전부 가져오기
            message_array = []
            for m in messages: # bytes list로 리턴된 걸 디코드하기
                m = m.decode('utf-8')
                m = literal_eval(m) # string dict를 dict로 만들기
                message_array.append(m)
            
            # dict가 담긴 array를 json array 형태로 저장.
            return message_array
        else:
            # db에서 메세지를 가지고오기
            messages = reversed(Message.objects.filter(livehole=room).order_by('-id')[:20])
            serializer = MessageSerializer(messages, many=True)
            # print("get_serialized_messages 디비쪽으로 들어옴 ")
            return serializer.data

    
    @database_sync_to_async
    def get_chat_room(self, room, group,con):
        res = con.hexists(group, room) # live hole을 캐시에서 가져올 수 있는지 확인
        # print("res : ", res)
        # print("get_chat_room에서 room : ", room)
        if res == 1:
            print("hexists 통과")
            livehole = con.hget(group,room).decode("utf-8") # channel num 불러오기
        else:
            livehole_qs = LiveHole.objects.get(id=room)
            livehole = livehole_qs.id
            livehole_h = con.hset(group,livehole,livehole)
            # print("hash cache set한 livehole : ", livehole_h)
        return livehole
