import time,random
from datetime import datetime,timezone
from locust import HttpUser, task, between,SequentialTaskSet,events
from websocket import create_connection
import gevent,json


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

class UserBehavior(SequentialTaskSet): # Sequence 활용해서 순차적인 플로우 고민
    hole_list = []
    token = ""
    token_list = []

    def on_start(self): #TaskSet마다 정의 가능
        self.login()

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
        # print("login res : ", res.json())
    @task
    def get_holes(self): # 전체 홀 조회
        print("전체 홀 보기")
        res = self.client.get("/api/hole")
        json_response_dict = res.json()
        # print("전체 홀 조회 res : ", res.json())
        for i in range(len(json_response_dict)):
            hole_id = json_response_dict[i]['id']
            self.hole_list.append(hole_id)
        # print("hole_list: ", self.hole_list)
    
    @task(2)
    def get_individual_hole(self):
        print("개별 홀 보기")
        indi_hole = str(self.hole_list.pop(0))
        response = self.client.get("/api/hole/read/"+indi_hole)

    @task
    def read_user_profile(self):
        print("개별 유저 프로필 조회")
        self.client.get(url="/api/user/read", headers={"authorization": "Token "+self.token})



    created_hole_list = {}
    @task
    def create_hole(self):
        print("홀 만들기")
        with self.client.post(
            url="/api/hole/create",
            headers= {"authorization": "Token "+self.token},
            json = {
                "title":"방만들기만들기만들기만들기", 
                "description": "만들기기기기기기",
                "reserve_date": str(datetime.now()),
                "target_demand": 0
            }
        ) as response:
            if response.status_code == 201:
                self.hole_id = response.json()['detail']['id']
                print("홀 만들기 성공")
                # print("self hole_id : ", self.hole_id)
            else:
                print("홀 만들기 실패")
    
    @task(2)
    def register_question(self):
        print("특정 홀에 사전 질문 등록")
        self.created_hole_list[self.hole_id] = []
        with self.client.post(
            url = "/api/hole/" + str(self.hole_id) +"/question/create",
            headers= {"authorization": "Token "+self.token},
            json = {
                "question":"질문합니다합니다합니다합니다합니다합니다합니다합니다합니다합니다합니다합니다합니다", 
             "is_voice": False,
             "is_answered": False,
            }
            ) as response:
            if response.status_code == 201:
                self.created_hole_list[self.hole_id].append(response.json()['detail']['id'])
                print("질문 등록 성공")
    
    @task
    def wish_hole(self):
        print("모집 세션 찜하기")
        # print("token_list : ", self.token_list)
        for i in range(len(self.token_list)):
            # print("token : ", self.token)
            if self.token == self.token_list[i]:
                continue
            else:
                with self.client.patch(
                    url="/api/reservation/hole/" + str(self.hole_id) +"/wish",
                    headers= {"authorization": "Token "+self.token_list[i]}
                    ) as response:
                    if response.json()['response'] == 'SUCCESS':
                        print("찜하기 성공")
                    else:
                        print("response : ",response.json())
                        print("찜하기 실패")
    
    @task
    def host_confirm_hole(self):
        print("홀 예약 확정하기")
        # print("self hole_id : ", self.hole_id)

        with self.client.patch(
            url="/api/reservation/hole/" + str(self.hole_id) +"/hostconfirm",
            headers= {"authorization": "Token "+self.token}
        ) as response:
            if response.json()['response'] == 'SUCCESS':
                print("예약 확정 성공")
            else:
                print("예약 확정 실패")
        
    @task
    def all_user_read(self):
        print("전체 유저 부르기")
        self.client.get("/api/user/all_read")

    @task
    def livehole_create(self): # 위에서 썼던 홀 id를 가져와야 할듯.
        print("라이브 홀 만들기")
        # print("self hole_id : ", self.hole_id)
        # self.hold_id 찍어보기
        self.channel_num = "thisisroom" + str(random.randint(10, 5000))
        with self.client.post(
            url="/api/hole/" + str(self.hole_id) +"/live/create",
            headers= {"authorization": "Token "+self.token},
            json={
                "channel_num" : self.channel_num,
                "host_uid": random.randint(100000,4000000)
            }
        ) as response:
            if response.json()['response'] == 'SUCCESS':
                print("라이브 홀 활성화 성공")
            else:
                print("라이브 홀 활성화 실패")


    @task
    def livehole_join(self):
        print("라이브 홀 조인")
        for i in range(len(self.token_list)):
            if self.token == self.token_list[i]:
                continue
            else:
                with self.client.put(
                    url="/api/hole/" + str(self.hole_id) +"/live/join/" + str(self.channel_num),
                    headers= {"Authorization": "Token "+self.token_list[i]},
                    json={
                        "uid" : random.randint(100000,4000000)
                    }
                ) as response:
                    # print("response : ", response.json())
                    if response.json()['response'] == 'SUCCESS':
                        print("라이브 홀 조인 성공")
                    else:
                        print("라이브 홀 조인 실패")
    @task
    def on_chat_start(self):
        WS_SERVER = 'wss://www.ask2live.me/ws/hole/' + self.channel_num +'/'
        print("채팅 열기")
        self.ws = create_connection(WS_SERVER)
        # print("웹소켓 커넥션")

        def _receive():
            print("채팅 받기")
            # print("웹소켓 리시브")
            while True:
                res = self.ws.recv()
                data = json.loads(res) #json을 deserialize 해줌.

                print("데이터 길이 : ", len(data))
                if len(data) >=1:
                    start_at = datetime.strptime(data[-1]['sent_timestamp'],'%Y-%m-%dT%H:%M:%S.%f%z')
                    name = data[-1]['sender']
                    fire_event_request(start_at, name, data)
                else:
                    continue
        gevent.spawn(_receive)

    #웹소켓 연결해서 채팅
    @task(2)
    def send(self):
        print("채팅 데이터 보내기")
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

    @task
    def update_question(self):
        print("라이브 홀 질문 답변 처리")
        # print("홀-질문 리스트 : ", self.created_hole_list )
        with self.client.patch(
            url = "/api/hole/" + str(self.hole_id) +"/question/update/" + str(self.created_hole_list[self.hole_id].pop(0)),
            headers= {"authorization": "Token "+self.token},
            json = {
            "is_answered": True,
            }
            ) as response:
            if response.json()['response'] == 'SUCCESS':
                print("질문 답변 처리 성공")
            else:
                print("질문 답변 처리 실패")
    @task(2)
    def read_question(self):
        print("라이브홀에서 질문 조회")
        self.client.get("/api/hole/" + str(self.hole_id)+ "/questions")

    
    @task
    def leave_live_hole(self):
        print("라이브 홀에서 나가기")
        for i in range(len(self.token_list)):
            if self.token == self.token_list[i]:
                continue
            else:
                with self.client.patch(
                    url="/api/hole/" + str(self.hole_id) +"/live/leave/" + str(self.channel_num),
                    headers= {"Authorization": "Token "+self.token_list[i]}
                ) as response:
                    # print("response : ", response.json())
                    if response.json()['response'] == 'SUCCESS':
                        print("라이브 홀 나가기 성공")
                    else:
                        print("라이브 홀 나가기 실패")


    # @events.test_stop.add_listener
    def on_stop(self): # 테스트 시 마스터 노드에서 한번만 수행
        print("A new test is ending")
        for i in range(len(self.token_list)):
            with self.client.post(
                url = "/api/user/logout",
                headers = {"Authorization": "Token "+self.token_list[i]}
            ) as response:
                if response.json()['response'] == 'SUCCESS':
                    print("로그아웃 성공")
                else:
                    print("로그아웃 실패")
        self.ws.close()

    # def on_quit(self):
    #     self.ws.close()
    # @task(3)
    # def view_items(self):
    #     for item_id in range(10):
    #         self.client.get(f"/item?id={item_id}", name="/item")
    #         time.sleep(1)

class WebsiteUser(HttpUser):
    tasks= [UserBehavior]
    wait_time = between(2,3)