from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404

from rest_framework import viewsets,status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated  # 로그인 권한
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Hole, LiveHole
from users import models as user_models
from hole_reservations import models as reserve_models
from .serializers import HoleSerializer,CreateLiveHoleSerializer
from django_mysql.models import ListF
# class HoleViewSet(viewsets.ModelViewSet):
#     queryset = Hole.objects.all()
#     serializer_class = HoleSerializer

# class HoleList(APIView):
#     # permission_classes = [IsAuthenticated]
#     """
#     게시물 생성
#     """
#     def post(self, request, format=None):
#         serializers = HoleSerializer(data=request.data)
#         if serializers.is_valid():
#             serializers.save()
#             return Response(serializers.data, status=status.HTTP_201_CREATED)
#         return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#     """
#     게시물 조회
#     """
#     def get(self, request, format=None):
#         queryset = Hole.objects.all()
#         serializers = HoleSerializer(queryset, many=True)
#         return Response(serializers.data)

# class HoleDetail(APIView):
#     permission_classes = [IsAuthenticated]
#     def get_object(self, pk):
#         try:
#             return Hole.objects.get(pk=pk)
#         except Hole.DoesNotExist:
#             raise Http404
    
#     """
#     특정 게시물 조회
#     /Hole/{pk}/
#     """
#     def get(self, request, pk):
#         holes = self.get_object(pk)
#         serializers = HoleSerializer(Hole)
#         return Response(serializers.data)

#     """
#     게시물 수정
#     """
#     def put(self, request, pk, format=None):
#         holes = self.get_object(pk)

#         user = request.user
#         if holes.host != user:
#             Response({'requset:', "You dont have permission to edit."})

#         serializers = HoleSerializer(Hole, data=request.data)
#         if serializers.is_valid():
#             serializers.save()
#             return Response(serializers.data)
#         return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#     """
#     게시물 삭제
#     """
#     def delete(self, request, pk, format=None):
#         holes = self.get_object(pk)

#         user = request.user
#         if holes.host != user:
#             Response({'requset:', "You dont have permission to edit."})
        
#         holes.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST',])
# @permission_classes((IsAuthenticated,))
def hole_create_view(request):
    
    account = request.user

    hole = Hole(host=account)

    serializer = HoleSerializer(hole, data=request.data)
    data = {}

    if serializer.is_valid():
        serializer.save()
        Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
# @permission_classes((IsAuthenticated,))
def hole_detail_view(request):
    holes = Hole.objects.all()
    serializer = HoleSerializer(holes, many=True)
    return Response(serializer.data)


@api_view(['PUT',])
# @permission_classes((IsAuthenticated,))
def hole_update_view(request, pk):

    try:
        hole = Hole.objects.get(pk=pk)
    except Hole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        user = request.user
        if hole.host != user:
            return Response({'response': "You don't have permission to edit this."})

        # 업데이트 대상 instance를 추가해야 함 (hole)
        serializer = HoleSerializer(hole, data=request.data)
        data = {}

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data["success"] = "update successful"
            return Response(data=data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE',])
# @permission_classes((IsAuthenticated,))
def hole_delete_view(request, pk):
    try:
        hole = Hole.objects.get(pk=pk)
    except Hole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if user != hole.host:
        return Response({'response': "You don't have permission to delete this."})

    operation = hole.delete()
    data = {}

    if operation:
        data["success"] = "delete successful"
    else:
        data["failure"] = "delete failed"

    return Response(data)


# 검색/정렬기능
class MypageHoleView(ListAPIView):

    queryset = Hole.objects.all()
    serializer_class = HoleSerializer
    # permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter,)
    search_fields = ('title', 'host__email')
    
    # 여기는 user가 생성한 hole만 보여주게 하는 것임
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset



@api_view(['GET',])
# @permission_classes((IsAuthenticated,))
def reserved_hole_detail_view(request):
    holes = Hole.objects.exclude(reserve_date__isnull=True).exclude(finish_date__isnull=True)
    print(holes)
    data = {}
    # reserved_holes = Reservation.objects.filter()
    # serializer = HoleSerializer(holes, many=True)
    return Response(data)

# Live Hole을 만드는 기능. room_number랑 uid 받을 거임.

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def live_hole_create_view(request,pk):
    account = request.user
    # print("account:",account)
    hole = Hole.objects.get(pk=pk)
    # print("hole:",hole)
    if request.method=="POST":
        is_host = request.data.get("is_host")
        # print("is_host:", is_host)
        data = {}
        if is_host == 'True':
            host_uid = request.data.get('host_uid')
            room_num = request.data.get('room_number')
            if room_num == None: # 에러 처리
                data['error_message'] = 'Room number does not exist'
                data['response'] = 'Error'
                return Response(data)
            # 정상적일 때, 시리얼라이즈로 json화 하기 - 일단 안함.
            # serializer = CreateLiveHoleSerializer(data=request.data)        
            # if serializer.is_valid():
                # hole의 status를 doing으로 변경하기, hole은 pk로 구분해야 할듯.
            # hole.update(status= STATUS_DOING)
            hole.status = 'DOING'
            hole.save()
            livehole=LiveHole.objects.create(host_uid=host_uid, room_number=room_num, hole=hole)
            # print(hole)
            # livehole.hole_id = hole.hole_id
            # livehole = serializer.save()
            livehole.save()
            print("livehole: ", livehole)
            data['response'] = 'live hole creation success'
            data['host_id'] = hole.host.pk
            data['host_uid'] = livehole.host_uid        
            return Response(data)
        else:
            data['error_message'] = 'Not Host'
            data['response'] = 'Error'
            return Response(data)

# audience list를 update하는 api
@api_view(['PUT',])
@permission_classes([])
def live_hole_update_view(request,room_num,pk):
    data = {}
    if request.method == 'PUT':
        is_host = request.POST.get("is_host")
        if is_host == 'False':
            uid = request.POST.get("uid")
            # livehole.audience_append(uid)
            livehole = LiveHole.objects.filter(room_number=room_num)   
            livehole.update(
                audience_list = ListF('audience_list').append(uid)
            )
            data['response'] = 'Audience uid append success'
            data['uid'] = uid
            return Response(data)
        else:
            data['error_message'] = 'Not Audience'
            data['response'] = 'Error'
            return Response(data)