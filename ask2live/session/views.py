from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404

from rest_framework import viewsets
from rest_framework.decorators import api_view

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Session
from .serializers import SessionSerializer

# class sessionViewSet(viewsets.ModelViewSet):
#     queryset = Session.objects.all()
#     serializer_class = SessionSerializer

class SessionList(APIView):
    """
    게시물 생성
    """
    def post(self, request, format=None):
        serializers = SessionSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

    """
    게시물 조회
    """
    def get(self, request, format=None):
        queryset = Session.objects.all()
        serializers = SessionSerializer(queryset, many=True)
        return Response(serializers.data)

class SessionDetail(APIView):
    def get_object(self, pk):
        try:
            return Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404
    
    """
    특정 게시물 조회
    /session/{pk}/
    """
    def get(self, request, pk):
        session = self.get_object(pk)
        serializers = SessionSerializer(session)
        return Response(serializers.data)

    """
    게시물 수정
    """
    def put(self, request, pk, format=None):
        session = self.get_object(pk)
        serializers = SessionSerializer(session, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    게시물 삭제
    """
    def delete(self, request, pk, format=None):
        session = self.get_object(pk)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST'])
# def session_list(request):
#     if request.method == 'POST':

#         serializers = SessionSerializer(data=request.data)
#         if serializers.is_valid(raise_exception=True):
#             serializers.save()
#             return Response(serializers.data)

#     else:
#         sessions = Session.objects.all()
#         serializers = SessionSerializer(sessions, many=True)
#         return Response(serializers.data)



# def index(request):

#     question_list = Question.objects.order_by('-create_date')
#     context = {'question_list': question_list}

#     return render(request, 'session/question_list.html', context)


# class MovieViewSet(viewsets.ModelViewSet):
    # queryset = Movie.objects.all()
    # serializer_class = MovieSerializer

