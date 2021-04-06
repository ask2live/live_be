from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404
from rest_framework import viewsets,status

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly  # 로그인 권한
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Hole, LiveHole,Participants,Question
from users import models as user_models
from hole_reservations.models import Reservation
from .serializers import LiveHoleSerializer,HoleListSerializer,HoleSerializer,ParticipantSerializer,QuestionSerializer
from hole_reservations.serializers import HoleReservationSerializer
from django_mysql.models import ListF
from datetime import datetime, timedelta
from dateutil.parser import parse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(methods=['post'], request_body=HoleSerializer, operation_description="POST /hole/create")
@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def hole_create_view(request): # hole 만드는 api, hole reservation도 같이 만들어져야 함.   
    print("DEBUG | Hole Create")
    if request.method == 'POST':
        # print("request : ", request)
        account = request.user
        user = user_models.User.objects.get(username=account)
        data = {}
        if user:
            reserve_date = request.data.get('reserve_date')
            # print("reserve_date : ", reserve_date)
            finish_date = parse(reserve_date) + timedelta(days=1)
            target_demand = request.data.get('target_demand')
            hole_serializer = HoleSerializer(context = {'request':request},data=request.data)
            # print("hole_serializer : ", hole_serializer)
            
            if hole_serializer.is_valid(): 
                hole_serializer.save()
                # print("hole_serializer : ", hole_serializer.data)
                pk = hole_serializer.data['id']
                # print("pk: ", pk)
                hole = Hole.objects.get(id=pk)
                # print("hole: ", hole)
                reservation_serializer = HoleReservationSerializer(
                    data={
                        "hole":hole.id, 
                        "reserve_date": reserve_date, 
                        "finish_date":finish_date, 
                        "target_demand":target_demand
                        })
                if reservation_serializer.is_valid():
                    reservation_serializer.save()
                    reservation_id = reservation_serializer.data['id']
                    reservation = Reservation.objects.get(id=reservation_id)
                    if int(target_demand) == 0:
                        reservation.status = 'CONFIRMED'
                        reservation.save()
                data['response'] = 'SUCCESS'
                data['detail'] = hole_serializer.data
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data['response'] = 'FAIL'
                data['detail'] = '유효한 정보가 아닙니다.'
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        # else: # 호스트권한이 없는 경우
        #     data['response'] = 'FAIL'
        #     data['detail'] = '호스트 권한이 없습니다.'
        #     return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def holes_view(request): #hole 상세정보 보는 api
    holes = Hole.objects.exclude(status="DONE") # DONE만 빼고 넘겨주기
    serializer = HoleListSerializer(holes, many=True)
    return Response(serializer.data)


@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def hole_read_view(request,pk): #hole 상세정보 보는 api
    data= {}
    try :
        hole = Hole.objects.get(id=pk)
    except Hole.DoesNotExist:
        data["response"] = "FAIL"
        data["detail"] = "조회 할 hole이 없습니다."
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = HoleListSerializer(hole)
    data['response'] = "SUCCESS"
    data['detail'] = serializer.data
    return Response(data)



@swagger_auto_schema(methods=['PATCH'], request_body=HoleSerializer, operation_description="PATCH /hole/update/{hole_id}")
@api_view(['PATCH',])
@permission_classes([IsAuthenticated,])
def hole_update_view(request, hole_id): # 특정 hole update하기
    print("DEBUG | Hole Update")
    data = {}
    # hole이 존재하는지 찾는다
    try:
        hole = Hole.objects.get(pk=hole_id)
    except Hole.DoesNotExist:
        data["response"] = "FAIL"
        data["detail"] = "수정 할 hole이 없습니다."
        return Response(status=status.HTTP_404_NOT_FOUND)
    # 본인이 만든 hole인지 검사한다
    user = request.user
    if hole.host != user:
        data["response"] = "FAIL"
        data["detail"] = "수정할 권한이 없습니다."
        return Response(data)
    # 업데이트 대상 instance를 추가해야 함 (hole)
    if request.method == "PATCH": #추후엔 PATCH로 바꾸는 것도 고려.
        hole_serializer = HoleSerializer(hole, data=request.data, partial=True)
        reservation_data = {}
        reserved_hole = Reservation.objects.get(hole=hole_id)
        reserve_date = request.data.get('reserve_date')
        guests = request.data.get('guests')
        if reserve_date:
            reservation_data['reserve_date'] = reserve_date
        target_demand = request.data.get('target_demand')
        print("target_demand : ", target_demand, flush=True)
        if target_demand >= 0:
            reservation_data['target_demand'] = target_demand
        print("reservation_data : ", reservation_data, flush=True)
        if hole_serializer.is_valid(raise_exception=True):

            hole_serializer.save()
            if reserve_date:
                hole.finish_date= hole_serializer.validated_data['reserve_date'] + timedelta(days=1)
            if reservation_data:
                reservation_serializer = HoleReservationSerializer(reserved_hole, context = {'request':request}, data=reservation_data, partial=True)
                if reservation_serializer.is_valid():
                    reservation_serializer.save()
            data["response"] = "SUCCESS"
            return Response(data=data)
        else:
            data["response"] = "FAIL"
            data['detail'] = '유효한 정보가 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE',])
@permission_classes([IsAuthenticated,])
def hole_delete_view(request, hole_id): # hole 삭제하는 api
    # hole이 존재하는지 찾는다
    data = {}
    try:
        hole = Hole.objects.get(pk=hole_id)
    except Hole.DoesNotExist:
        data["response"] = "FAIL"
        data["detail"] = "삭제할 hole이 없습니다."
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    # 본인이 만든 hole인지 검사한다
    user = request.user
    if user != hole.host:
        data["response"] = "FAIL"
        data["detail"] = "삭제할 권한이 없습니다."
        return Response(data)
    # 예약 내역이 있으면 함께 지운다
    try:
        reserved_hole = reserve_models.Reservation.objects.get(hole=hole_id)
        reserved_hole.delete()
    except:
        pass
    operation = hole.delete()
    # print("operations : ", operation)
    if operation:
        data["response"] = "SUCCESS"
    else:
        data["response"] = "FAIL"
    return Response(data)


@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def reserved_hole_detail_view(request): # 예약된 hole만 조회하는 api
    reserved_holes = Hole.objects.exclude(reserve_date__isnull=True).exclude(finish_date__isnull=True)
    serializer = HoleSerializer(reserved_holes, many=True)
    
    return Response(serializer.data)


class HoleSearchView(ListAPIView): # hole을 찾는 api
    # queryset = Hole.objects.all()
    serializer_class = HoleSerializer
    authentication_classes = ([])
    permission_classes = ([])

    def get_context_data(self, *args, **kwargs): # context data 공부하기
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET('q')
        # print(context)
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            self.count = len(query)
            return Hole.objects.search(query=query)
        return Hole.objects.none()


# Live Hole을 만드는 기능. room_number랑 uid 받을 거임.
@swagger_auto_schema(methods=['POST'], request_body=LiveHoleSerializer, operation_description="POST /hole/update/{hole_id}")
@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def live_hole_create_view(request,pk):
    print("DEBUG | Live Hole Create")
    serializer_class = ParticipantSerializer
    user = request.user
    # print("account:",account)
    hole = Hole.objects.get(pk=pk)
    if request.method=="POST":
        data = {}
        if user.username == hole.host.username: # 호스트일경우
            host_uid = request.data.get('host_uid')
            channel_num = request.data.get('channel_num')
            if channel_num == None: # 에러 처리
                data['response'] = 'FAIL'
                data['detail'] = 'Channel number does not exist.'
                return Response(data)
            hole.status = 'DOING'
            hole.host.uid = host_uid # 호스트의 uid도 User 모델에 저장
            hole.save()
            livehole=LiveHole.objects.create(host_uid=host_uid, hole=hole, id=channel_num)
            livehole.save()
            serializer= serializer_class(data= {'livehole' : livehole.id, 'user': user.id})
            if serializer.is_valid():
                serializer.save()
            data['response'] = 'SUCCESS'
            data['detail'] = {}
            data['detail']['host_id'] = hole.host.pk
            data['detail']['host_uid'] = livehole.host_uid 
            if hole.host.profile_image:
                data['detail']['host_profile_image_url'] = hole.host.get_photo_url()
            else :
                data['detail']['host_profile_image_url'] = None
            return Response(data)
        else:
            data['response'] = 'FAIL'
            data['detail'] = 'You are not a host.'
            return Response(data)

# audience list를 update하는 api
@swagger_auto_schema(methods=['PUT'], request_body=LiveHoleSerializer, operation_description="PUT /hole/update/{hole_id}")
@api_view(['PUT',])
@permission_classes([])
def live_hole_update_view(request,pk,channel_num): # 우리는 url로 channel_num을 넘겨줌.
    serializer_class = ParticipantSerializer
    if request.method == 'PUT':
        data = {}
        user = request.user
        livehole = LiveHole.objects.filter(id=channel_num)  
        # print("livehole : ", livehole) 
        serializer= serializer_class(data= {'livehole' : livehole[0].id, 'user': user.id}) # 참가자 목록에 넣기.
        if user.username != livehole[0].hole.host.username: # host가 아니라 audience인 경우
            uid = request.data.get("uid")
            uid_user = user_models.User.objects.get(username=user)
            uid_user.uid = uid
            uid_user.save()
            livehole.update(
                audience_uids = ListF('audience_uids').append(uid)
            )
            if serializer.is_valid():
                serializer.save()
            data['response'] = 'SUCCESS'
            data['detail'] = {}
            data['detail']['audience_uid'] = uid
            data['detail']['audience_username'] = user.username
            return Response(data,status=status.HTTP_200_OK)
        else:
            data['response'] = 'FAIL'
            data['detail'] = '호스트는 본인이 만든 홀에 조인 할 수 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH',])
@permission_classes([])
def live_hole_leave_view(request,pk,channel_num): # 우리는 url로 channel_num을 넘겨줌.
    data = {}
    print("DEBUG | Live Hole Leave")
    if request.method == 'PATCH':
        # print("request : ", request)
        user = request.user
        # print("request user : ", request.user)
        participant = Participants.objects.get(livehole=channel_num, user=user,leaved__isnull=True)
        serializer = ParticipantSerializer(participant, data={'leaved':datetime.now()}, partial=True)
        # audience가 나갈 경우 audience uid를 지워야 함.
        if serializer.is_valid():
            livehole = LiveHole.objects.get(id=channel_num)
            if user.username == livehole.hole.host.username: # 호스트인 경우
                livehole.hole.status = 'DONE'
                livehole.hole.finish_date = timezone.now()
                livehole.hole.save()
                # TODO : 방이 폭파되는거라 게스트도 다 leave가 찍혀야 함..!
            serializer.save()
            data['response'] = 'SUCCESS'
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def live_hole_read_view(request,channel_num): # 현재 라이브하고있는 그 홀의 정보륿 불러와야 할듯. 그리고 leave 안 된 사람만!
    try:
        livehole = LiveHole.objects.get(id=channel_num)
        # filter는 여러개 가지고올 수 있고, get은 1개만 가져온다.
        # print("live_hole:",livehole)
    except LiveHole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {}
    participant = Participants.objects.filter(livehole=livehole.id, leaved__isnull=True)
    if request.method == 'GET':
        livehole_serializer = LiveHoleSerializer(livehole)
        participant_serializer = ParticipantSerializer(participant,many=True)
        data['response'] = 'SUCCESS'
        data['detail'] = {}
        data['detail']['livehole'] = livehole_serializer.data
        data['detail']['participant'] = participant_serializer.data
        return Response(data, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=['post'], request_body=QuestionSerializer, operation_description="POST /question/create")
@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def hole_question_register_view(request,pk):
    hole = Hole.objects.get(id=pk)
    serializer = QuestionSerializer(context = {'request':request},data=request.data)
    # print("serailizer", serializer)
    data = {}
    if serializer.is_valid():
        serializer.save(hole=hole)
        data['response'] = 'SUCCESS'
        data['detail'] = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        data['response'] = 'FAIL'
        data['detail'] = 'Invalid data'
        return Response(data, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['PATCH',])
@permission_classes([])
def hole_question_update_view(request,question_id, pk=None):
    data = {}
    # hole이 존재하는지 찾는다
    try:
        question = Question.objects.get(id=question_id)
    except question.DoesNotExist:
        data["response"] = "FAIL"
        data["detail"] = "수정 할 질문이 없습니다."
        return Response(status=status.HTTP_404_NOT_FOUND)
    # 본인이 만든 hole인지 검사한다
    if request.method == 'PATCH':
        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data["response"] = "SUCCESS"
            return Response(data=data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE',])
@permission_classes([IsAuthenticated])
def hole_question_delete_view(request,question_id,pk=None): #등록한 질문을 본인이 지울 수 있는 api
    data = {}
    try:
        question = Question.objects.get(id=question_id)
    except question.DoesNotExist:
        data["response"] = "FAIL"
        data["detail"] = "삭제할 질문이 없습니다."
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    # 본인이 만든 hole인지 검사한다
    user = request.user
    if user != question.user:
        data["response"] = "FAIL"
        data["detail"] = "삭제할 권한이 없습니다."
        return Response(data)
    operation = question.delete()
    # print("operations : ", operation)
    if operation:
        data["response"] = "SUCCESS"
    else:
        data["response"] = "FAIL"
        data["detail"] = "삭제를 실패했습니다."
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def hole_question_allread_view(request,pk):
    data={}
    try :
        hole = Hole.objects.get(id=pk)
    except hole.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '질문을 불러 올 방이 없습니다.'
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    questions = Question.objects.filter(hole=hole)
    if request.method == 'GET':
        serializer = QuestionSerializer(questions, many=True)
        data['response'] = 'SUCCESS'
        data['detail'] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([])
def hole_wish_view(request,pk):
    data={}
    try:
        hole = Hole.objects.get(id=pk)
    except hole.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '예약 요청을 할 방이 없습니다.'
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PATCH':
        reservation = Reservation.objects.get(hole=hole)
        user = request.user
        if user == hole.host:
            data['response'] = 'FAIL'
            data['detail'] = '호스트는 예약 신청을 할 수 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        reservation.current_demand +=1
        # print("reservation : ", reservation)
        # print("reservation : ", reservation.guests)
        wish_user_obj = user_models.User.objects.get(username=user)
        if wish_user_obj.hole_reservations.filter(id=reservation.id, guests=user).exists(): # many to many field의 reverse accessor 활용
            data['response'] = 'FAIL'
            data['detail'] = '중복 신청은 할 수 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            reservation.guests.add(user)
        if reservation.current_demand == reservation.target_demand:
            reservation.status = "CONFIRMED"
        reservation.save()
        data["response"] = "SUCCESS"
        return Response(data=data)
        
@api_view(['PATCH'])
@permission_classes([])
def hole_wish_cancel_view(request,pk):
    data={}
    try:
        hole = Hole.objects.get(id=pk)
    except hole.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '예약 취소 요청을 할 방이 없습니다.'
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PATCH':
        reservation = Reservation.objects.get(hole=hole)
        user = request.user
        if user == hole.host:
            data['response'] = 'FAIL'
            data['detail'] = '호스트는 예약 취소 신청을 할 수 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        reservation.current_demand -=1
        # print("reservation : ", reservation.guests) # 왜 users.User.None 로 찍히지?
        wish_user_obj = user_models.User.objects.get(username=user)
        target_user = wish_user_obj.hole_reservations.filter(guests=user)
        if target_user.exists(): # many to many field의 reverse accessor 활용
            reservation.guests.remove(user)
        else:
            data['response'] = 'FAIL'
            data['detail'] = '해당 예약 리스트에 유저가 없습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        if reservation.current_demand < reservation.target_demand:
            reservation.status = "PENDING"
        reservation.save()
        data["response"] = "SUCCESS"
        return Response(data=data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,])
def host_hole_confirm_view(request,pk):
    # print("request : ", request)
    # print("request user : ", request.user)
    data={}
    try:
        hole = Hole.objects.get(id=pk)
    except hole.DoesNotExist:
        data['response'] = 'FAIL'
        data['detail'] = '호스트가 예약 확정 요청을 할 방이 없습니다.'
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        reservation = Reservation.objects.get(hole=hole)
        user = request.user
        if user != hole.host:
            data['response'] = 'FAIL'
            data['detail'] = '호스트만 예약 확정을 할 수 있습니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)        
        if reservation.status != 'CONFIRMED':
            data['response'] = 'FAIL'
            data['detail'] = '예약 세션이 confirmed 상태가 아닙니다.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 
        reservation.status = "HOST_CONFIRMED"
        reservation.save()
        # 상태가 바뀌었으니 예약요청한 게스트에게 메일 보내기가 구현되어야 함.
        data["response"] = "SUCCESS"
        return Response(data=data)