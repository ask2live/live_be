from locust import HttpUser, events, task, TaskSet, between,SequentialTaskSet
from websocket import create_connection
import gevent
import time,random
from datetime import datetime,timezone
import json
WS_SERVER_URL = 'wss://www.ask2live.me/ws/hole/7135/'

class UserBehavior(SequentialTaskSet):
    token = ""
    token_list = []
    def on_start(self): #TaskSet마다 정의 가능
        self.login()
        print("채팅 열기")
        self.ws = create_connection(WS_SERVER_URL)
        def _receive():
            print("채팅 받기")
            while True:
                res = self.ws.recv()
                data = json.loads(res) #json을 deserialize 해줌.

                # print("데이터 길이 : ", len(data))
                if len(data) >=1:
                    start_at = datetime.strptime(data[-1]['sent_timestamp'],'%Y-%m-%d %H:%M:%S.%f')
                    end_at = datetime.now()
                    name = 'ws/hole/7135'
                    events.request_success.fire(
                        request_type='Websocket Receive Message',
                        name=name,
                        response_time=abs(int((end_at - start_at).total_seconds() * 1000)),
                        response_length=len(data),
                    )
                    end_at = datetime.now(timezone.utc).astimezone()
                else:
                    continue
        gevent.spawn(_receive)

    def login(self):
        print("로그인 하기")
        # 처음에는 한명만 로그인 하지만 login 세트를 하나씩 돌아가며 로그인하게 개선해보자.
        username = "foo" + str(random.randint(1, 5000))
        with self.client.post(
            "/api/user/login", 
            json={
                "username": username, 
                "password":"bar"
                }
            ) as response:
            self.token = response.json()['detail']['token']
            self.token_list.append(self.token)    

    #웹소켓 연결해서 채팅
    @task(2)
    def send(self):
        print("채팅 데이터 보내기")
        start_at = time.time()
        # 특정한 channelNum 정해서 들어가기
        name = 'ws/hole/7135'
        body = json.dumps({
            'command': 'new_message',
            'data': {
                'text': 'hello world111',
                'sender': 'foo4098',
            }            
            }) # json을 serialize 해줌. 서버에 보냄
        ss = self.ws.send(body)
        events.request_success.fire(
            request_type='Websocket Send Message',
            name=name,
            response_time=int((time.time() - start_at) * 1000000),
            response_length=len(body),
        )
        # time.sleep(10)
        # self.wait()


    def on_quit(self):
        self.ws.close()

class WebsiteUser(HttpUser):
    tasks= [UserBehavior]
    wait_time = between(2,3)