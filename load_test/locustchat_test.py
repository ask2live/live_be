from locust import HttpUser, events, task, TaskSet, between,SequentialTaskSet
from websocket import create_connection
import gevent
import time,random
from datetime import datetime,timezone
import json
WS_SERVER_URL = 'wss://www.ask2live.me/ws/hole/4335/'

# def fire_event_request(start_at, name, body):
#     res_time = int(((datetime.now(timezone.utc) - start_at)).total_seconds())
#     # print("res time : ", res_time)
#     # print("body : ", body)
#     events.request_success.fire(
#         request_type='Websocket Receive Message',
#         name=name,
#         response_time=res_time,
#         response_length=len(body),
#     )


class UserBehavior(SequentialTaskSet):
    token = ""
    token_list = []
    def on_start(self): #TaskSet마다 정의 가능
        self.login()
        # WS_SERVER = 'wss://www.ask2live.me/ws/hole/' + self.channel_num +'/'
        print("채팅 열기")
        self.ws = create_connection(WS_SERVER_URL)
        def _receive():
            print("채팅 받기")
            # print("웹소켓 리시브")
            while True:
                res = self.ws.recv()
                data = json.loads(res) #json을 deserialize 해줌.

                # print("데이터 : ", data)
                print("데이터 길이 : ", len(data))
                if len(data) >=1:
                    # for i in range(len(data)):a
                    #     print("sent_timestamp : ",data[i]['sent_timestamp'] )
                    start_at = datetime.strptime(data[-1]['sent_timestamp'],'%Y-%m-%dT%H:%M:%S.%f%z')
                    end_at = time.time()
                    # end_at = datetime.now(timezone.utc).astimezone()
                    # end_at1 = datetime.now()
                    # name = data[-1]['livehole']
                    # print("받을 때 end_at : ", end_at)
                    # print("end_at1 : ", end_at)
                    # print("받을 때 start_at : ", start_at)
                    # print("받을 때 둘의 차 : ", (end_at - start_at))
                    # print("받을 때 둘의 차 초단위 : ", int((end_at - start_at).total_seconds()))
                    name = 'ws/hole/5783'
                    # print("time : ", data['start_at'])
                    response_time = int((end_at - start_at) * 1000000)
                    events.request_success.fire(
                        request_type='Websocket Receive Message',
                        name=name,
                        # response_time=abs(int((end_at - start_at).total_seconds() * 1000)),
                        response_time=response_time,
                        response_length=len(data),
                    )
                    end_at = datetime.now(timezone.utc).astimezone()
                    # print("end_at 2 : ", end_at)
                    # res_time = int((datetime.now(timezone.utc).astimezone()- start_at).total_seconds())
                    # print("받을 때 res time : ", res_time)
                    # fire_event_request(start_at, name, data)
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

    # @task
    # def on_chat_start(self):
    #     # WS_SERVER = 'wss://www.ask2live.me/ws/hole/' + self.channel_num +'/'
    #     print("채팅 열기")
    #     self.ws = create_connection(WS_SERVER_URL)
    #     # print("웹소켓 커넥션")

    #     def _receive():
    #         print("채팅 받기")
    #         # print("웹소켓 리시브")
    #         while True:
    #             res = self.ws.recv()
    #             data = json.loads(res) #json을 deserialize 해줌.

    #             print("데이터 : ", data)
    #             print("데이터 길이 : ", len(data))
    #             if len(data) >=1:
    #                 for i in range(len(data)):
    #                     print("sent_timestamp : ",data[i]['sent_timestamp'] )
    #                 start_at = datetime.strptime(data[-1]['sent_timestamp'],'%Y-%m-%dT%H:%M:%S.%f%z')
    #                 # end_at = time.time()
    #                 end_at = datetime.now(timezone.utc).astimezone()
    #                 # name = data[-1]['livehole']
    #                 print("end_at : ", end_at)
    #                 # print("start_at : ", start_at)
    #                 name = 'ws/hole/5783'
    #                 # print("time : ", data['start_at'])
    #                 # response_time = int((end_at - start_at) * 1000000)
    #                 events.request_success.fire(
    #                     request_type='Websocket Receive Message',
    #                     name=name,
    #                     response_time=int((datetime.now(timezone.utc).astimezone() - start_at).total_seconds() * 1000),
    #                     # response_time=response_time,
    #                     response_length=len(data),
    #                 )
    #                 end_at = datetime.now(timezone.utc).astimezone()
    #                 print("end_at 2 : ", end_at)
    #                 # res_time = int((datetime.now(timezone.utc).astimezone()- start_at).total_seconds())
    #                 # print("받을 때 res time : ", res_time)
    #                 # fire_event_request(start_at, name, data)
    #             else:
    #                 continue
    #     gevent.spawn(_receive)


    #웹소켓 연결해서 채팅
    @task(2)
    def send(self):
        print("채팅 데이터 보내기")
        # min_wait = 2000
        # max_wait = 5000
        # start_at= datetime.now(timezone.utc).astimezone()
        start_at = time.time()
        # name = self.channel_num
        name = 'ws/hole/5783'
        body = json.dumps({
            'command': 'new_message',
            'data': {
                'text': 'hello world111',
                'sender': 'foo2439',
                'start_at' : start_at
            }            
            }) # json을 serialize 해줌. 서버에 보냄
        self.ws.send(body)
        print("send 시 start_at : ", start_at)
        print("send 시 end_at : ", time.time())
        print("둘의 차이 : ", (time.time() - start_at))
        events.request_success.fire(
            request_type='Websocket Send Message',
            name=name,
            # response_time=int((datetime.now(timezone.utc).astimezone()- start_at).total_seconds()),
            response_time=int((time.time() - start_at) * 1000000),
            response_length=len(body),
        )
        # res_time = int((datetime.now(timezone.utc).astimezone()- start_at).total_seconds())
        # print("send 할 때 res time : ", res_time)
        # self._sleep(randint(min_wait, max_wait))
        # time.sleep(10)
        # self.wait()


    def on_quit(self):
        self.ws.close()

class WebsiteUser(HttpUser):
    tasks= [UserBehavior]
    wait_time = between(2,3)