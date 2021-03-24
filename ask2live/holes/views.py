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

from .models import Hole, LiveHole,Participants
from users import models as user_models
from hole_reservations import models as reserve_models
from .serializers import LiveHoleSerializer,HoleListSerializer,HoleSerializer,ParticipantSerializer
from django_mysql.models import ListF

@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def hole_create_view(request): # hole 만드는 api
    account = request.user
    # hole = Hole(host=account)
    serializer = HoleSerializer(context = {'request':request},data=request.data)
    data = {}
    if serializer.is_valid():
        # print("serializer : ", serializer.validated_data)
        serializer.save()
        data['response'] = 'SUCCESS'
        data['detail'] = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def hole_detail_view(request): #hole 상세정보 보는 api
    holes = Hole.objects.exclude(status="DONE") # DONE만 빼고 넘겨주기
    serializer = HoleListSerializer(holes, many=True)
    return Response(serializer.data)


@api_view(['PATCH',])
@permission_classes([IsAuthenticated,])
def hole_update_view(request, hole_id): # 특정 hole update하기
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
        serializer = HoleSerializer(hole, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data["response"] = "SUCCESS"
            return Response(data=data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        print("reserved hole : ", reserved_hole)
        reserved_hole.delete()
    except:
        pass
    operation = hole.delete()
    print("operations : ", operation)
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
        print(context)
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            self.count = len(query)
            return Hole.objects.search(query=query)
        return Hole.objects.none()


# Live Hole을 만드는 기능. room_number랑 uid 받을 거임.
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def live_hole_create_view(request,pk):
    account = request.user
    # print("account:",account)
    hole = Hole.objects.get(pk=pk)
    if request.method=="POST":
        is_host = request.data.get("is_host")
        data = {}
        if is_host == 'True':
            host_uid = request.data.get('host_uid')
            channel_num = request.data.get('channel_num')
            if channel_num == None: # 에러 처리
                data['response'] = 'FAIL'
                data['detail'] = 'Channel number does not exist.'
                return Response(data)
            # 정상적일 때, 시리얼라이즈로 json화 하기 - 일단 안함.
            # serializer = CreateLiveHoleSerializer(data=request.data)        
            # if serializer.is_valid():
                # hole의 status를 doing으로 변경하기, hole은 pk로 구분해야 할듯.
            # hole.update(status= STATUS_DOING)
            hole.status = 'DOING'
            hole.save()
            livehole=LiveHole.objects.create(host_uid=host_uid, hole=hole, id=channel_num)
            livehole.save()
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
@api_view(['PUT',])
@permission_classes([])
def live_hole_update_view(request,pk,channel_num): # 우리는 url로 channel_num을 넘겨줌.
    serializer_class = ParticipantSerializer
    if request.method == 'PUT':
        data = {}
        user = request.user
        # is_host = request.POST.get("is_host")
        livehole = LiveHole.objects.filter(id=channel_num)   
        serializer= serializer_class(data= {'livehole' : livehole[0].id, 'user': user.id}) # 참가자 목록에 넣기.
        if user.email != livehole[0].hole.host.email: # host가 아니라 audience인 경우
        # if is_host == 'False':
            uid = request.POST.get("uid")
            livehole.update(
                audience_uids = ListF('audience_uids').append(uid)
            )
            if serializer.is_valid():
                serializer.save()
            data['response'] = 'SUCCESS'
            data['detail'] = {}
            data['detail']['audience_uid'] = uid
            data['detail']['audience_nickname'] = user.nickname
            return Response(data,status=status.HTTP_200_OK)
        else:
            data['response'] = 'FAIL'
            data['detail'] = 'You cannot join a hole you made.'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET',])
@permission_classes([IsAuthenticatedOrReadOnly,])
def live_hole_read_view(request,channel_num): # 현재 라이브하고있는 그 홀의 정보륿 불러와야 할듯. 그리고 leave 안 된 사람만!
    try:
        livehole = LiveHole.objects.get(id=channel_num)
        # filter는 여러개 가지고올 수 있고, get은 1개만 가져온다.
        print("live_hole:",livehole)
    except LiveHole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {}
    participant = Participants.objects.filter(livehole=livehole.id, leaved__isnull=True)
    if request.method == 'GET':
        livehole_serializer = LiveHoleSerializer(livehole)
        participant_serializer = ParticipantSerializer(participant,many=True)
        print("livehole_serializer.data",livehole_serializer.data)
        print("participant_serializer.data",participant_serializer.data)
        data['livehole'] = livehole_serializer.data
        data['participant'] = participant_serializer.data
        return Response(data, status=status.HTTP_200_OK)
