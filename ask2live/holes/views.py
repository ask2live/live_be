from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import IsAuthenticated  # 로그인 권한

from .models import Hole
from .serializers import HoleSerializer

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
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
def hole_detail_view(request):

    # try:
    #     hole = Hole.objects.get(pk=pk)
    # except Hole.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    holes = Hole.objects.all()
    serializer = HoleSerializer(holes, many=True)
    return Response(serializer.data)


@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def hole_update_view(request, pk):

    try:
        hole = Hole.objects.get(pk=pk)
    except Hole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if hole.host != user:
        return Response({'response': "You don't have permission to edit this."})

    serializer = HoleSerializer(data=request.data)
    data = {}

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        data["success"] = "update successful"
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE',])
@permission_classes((IsAuthenticated,))
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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

