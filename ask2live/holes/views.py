from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404

from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import IsAuthenticated  # 로그인 권한
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Hole
from .serializers import HoleSerializer

from users import models as user_models
from hole_reservations import models as reserve_models

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
def hole_update_view(request, hole_id):

    # hole이 존재하는지 찾는다
    try:
        hole = Hole.objects.get(pk=hole_id)
    except Hole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # 본인이 만든 hole인지 검사한다
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
def hole_delete_view(request, hole_id):

    # hole이 존재하는지 찾는다
    try:
        hole = Hole.objects.get(pk=hole_id)
    except Hole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # 본인이 만든 hole인지 검사한다
    user = request.user
    if user != hole.host:
        return Response({'response': "You don't have permission to delete this."})

    # 예약 내역이 있으면 함께 지운다
    try:
        reserved_hole = reserve_models.Reservation.objects.get(hole=hole_id)
        reserved_hole.delete()
    except:
        pass

    operation = hole.delete()
    data = {}
    
    if operation:
        data["success"] = "delete successful"
    else:
        data["failure"] = "delete failed"

    return Response(data)



@api_view(['GET',])
# @permission_classes((IsAuthenticated,))
def reserved_hole_detail_view(request):
    reserved_holes = Hole.objects.exclude(reserve_date__isnull=True).exclude(finish_date__isnull=True)
    serializer = HoleSerializer(reserved_holes, many=True)
    
    return Response(serializer.data)


class HoleSearchView(ListAPIView):

    # queryset = Hole.objects.all()
    serializer_class = HoleSerializer
    # filterset_fields = ['status']

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context['count'] = self.count or 0
    #     context['query'] = self.request.GET('q')
    #     print(context)
    #     return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            self.count = len(query)
            return Hole.objects.search(query=query)
        return Hole.objects.none()
    