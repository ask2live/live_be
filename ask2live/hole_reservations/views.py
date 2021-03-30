from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from django.views.generic import FormView
from holes.models import Hole
from holes.serializers import HoleSerializer
from users.models import User
from .serializers import HoleReservationSerializer
from .models import Reservation
from holes.models import Hole
from django import forms

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ReservationList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HoleReservationSerializer
    # model = Reservation
    # paginate_by = 10

    def get_queryset(self):
        queryset = Reservation.objects.all()
        # queryset = queryset.filter(user=request.user)
        return queryset

# reserve_wish_view 만들기 (PATCH로 만들어야 하나?)


@api_view(['PUT',])
# @permission_classes((IsAuthenticated,))
def reserve_update_view(request, hole_id):

    # if request.method == 'PUT':
        # user = request.user
        # if hole.host != user:
            # return Response({'response': "You don't have permission to edit this."})

    updated_hole = Hole.objects.get(pk=hole_id)
    reserved_hole = Reservation.objects.get(hole=hole_id)
    serializer = HoleReservationSerializer(reserved_hole, data=request.data)

    if serializer.is_valid():
        start = serializer.validated_data['reserve_start_date']
        end = serializer.validated_data['finish_date']

        updated_hole.reserve_date = start
        updated_hole.finish_date = end
        updated_hole.save()

        serializer.save()
        return Response(serializer.data)

    else:
        return Response(serializer.errors)


@api_view(['DELETE',])
# @permission_classes((IsAuthenticated,))
def reserve_delete_view(request, hole_id):
    updated_hole = Hole.objects.get(pk=hole_id)

    user = request.user
    if user != updated_hole.host:
        return Response({'response': "You don't have permission to delete this."})
    
    reserved_hole = Reservation.objects.get(hole=hole_id)
    data={}

    # 기존 hole 정보 변경
    updated_hole.reserve_date = None
    updated_hole.finish_date = None
    updated_hole.status = Hole.STATUS_NOTSTART
    updated_hole.save()

    operation = reserved_hole.delete()
    
    if operation:
        data["success"] = "delete successful"
    else:
        data["failure"] = "delete failed"
    
    return Response(data)