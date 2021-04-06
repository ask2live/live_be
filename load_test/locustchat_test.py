from locust import HttpUser, events, task, TaskSet, between
from websocket import create_connection
import gevent
import time
from datetime import datetime,timezone
import json
WS_SERVER = 'wss://www.ask2live.me/ws/hole/thisisroomlocust/'

def fire_event_request(start_at, name, body):
    res_time = int(((datetime.now(timezone.utc) - start_at)).total_seconds())
    # print("res time : ", res_time)
    # print("body : ", body)
    events.request_success.fire(
        request_type='Websocket Receive Message',
        name=name,
        response_time=res_time,
        response_length=len(body),
    )


class QuickStartUser(TaskSet):
    @task
    def hello_world(self):
        print("GET API")
        self.client.get("/api/hole")

    @task
    def send(self):
        print("데이터 보내기")
        min_wait = 2000
        max_wait = 5000
        body = json.dumps({
            'command': 'new_message',
            'data': {
                'text': 'hello world111',
                'sender': 'foo2439' 
            }            
            }) # json을 serialize 해줌. 서버에 보냄
        self.ws.send(body)
        # self._sleep(randint(min_wait, max_wait))
        # time.sleep(10)
        self.wait()

    def on_start(self):
        self.ws = create_connection(WS_SERVER)
        # print("웹소켓 커넥션")

        def _receive():
            # print("웹소켓 리시브")
            while True:
                res = self.ws.recv()
                # print("json res : ", res)
                data = json.loads(res) #json을 deserialize 해줌.
                # print("data : ",data )
                # sent_timestamp = datetime.strptime(data[0]['sent_timestamp'],'%m.%d.%YT%H:%M:%S.%f')
                # sent_timestamp = data[0]['sent_timestamp']
                print("데이터 길이 : ", len(data))
                # for i in range(len(data)):
                if len(data) >=2:
                    start_at = datetime.strptime(data[-1]['sent_timestamp'],'%Y-%m-%dT%H:%M:%S.%f%z')
                    name = data[-1]['sender']
                else:
                    start_at = datetime.strptime(data[0]['sent_timestamp'],'%Y-%m-%dT%H:%M:%S.%f%z')
                    name = data[0]['sender']
                fire_event_request(start_at, name, data)
        gevent.spawn(_receive)

    def on_quit(self):
        self.ws.close()

class WebsiteUser(HttpUser):
    tasks= [QuickStartUser]
    wait_time = between(2,3)