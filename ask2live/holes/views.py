from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404

from rest_framework import viewsets
from rest_framework.decorators import api_view

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Hole
from .serializers import HoleSerializer

# class HoleViewSet(viewsets.ModelViewSet):
#     queryset = Hole.objects.all()
#     serializer_class = HoleSerializer

class HoleList(APIView):
    """
    게시물 생성
    """
    def post(self, request, format=None):
        serializers = HoleSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

    """
    게시물 조회
    """
    def get(self, request, format=None):
        queryset = Hole.objects.all()
        serializers = HoleSerializer(queryset, many=True)
        return Response(serializers.data)

class HoleDetail(APIView):
    def get_object(self, pk):
        try:
            return Hole.objects.get(pk=pk)
        except Hole.DoesNotExist:
            raise Http404
    
    """
    특정 게시물 조회
    /Hole/{pk}/
    """
    def get(self, request, pk):
        holes = self.get_object(pk)
        serializers = HoleSerializer(Hole)
        return Response(serializers.data)

    """
    게시물 수정
    """
    def put(self, request, pk, format=None):
        holes = self.get_object(pk)
        serializers = HoleSerializer(Hole, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    게시물 삭제
    """
    def delete(self, request, pk, format=None):
        holes = self.get_object(pk)
        holes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST'])
# def Hole_list(request):
#     if request.method == 'POST':

#         serializers = HoleSerializer(data=request.data)
#         if serializers.is_valid(raise_exception=True):
#             serializers.save()
#             return Response(serializers.data)

#     else:
#         Holes = Hole.objects.all()
#         serializers = HoleSerializer(Holes, many=True)
#         return Response(serializers.data)



# def index(request):

#     question_list = Question.objects.order_by('-create_date')
#     context = {'question_list': question_list}

#     return render(request, 'Hole/question_list.html', context)


# class MovieViewSet(viewsets.ModelViewSet):
    # queryset = Movie.objects.all()
    # serializer_class = MovieSerializer

