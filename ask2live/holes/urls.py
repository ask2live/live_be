from django.urls import include, path

from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    hole_create_view,
    hole_detail_view,
    hole_update_view,
    hole_delete_view,
    reserved_hole_detail_view,
    HoleSearchView,
    live_hole_update_view,
    live_hole_create_view,
    live_hole_leave_view,
    live_hole_read_view,
    hole_question_register_view,
    hole_question_update_view,
    hole_question_delete_view,
    hole_question_allread_view,
)
app_name = 'holes'

urlpatterns = [
    path('', hole_detail_view, name="detail"),
    # path('all', hole_detail_view, name="detail"), # 위에거 이거로 교체하기
    path('<int:pk>/live/join/<str:channel_num>', live_hole_update_view, name="live_join"),
    path('<int:pk>/live/leave/<str:channel_num>', live_hole_leave_view, name="live_leave"),
    path('create', hole_create_view, name="create"),
    path('update/<int:hole_id>', hole_update_view, name="update"),
    path('delete/<int:hole_id>', hole_delete_view, name="delete"),
    path('<int:pk>/live/create', live_hole_create_view, name='live_create'),
    path('live/read/<str:channel_num>', live_hole_read_view, name='live_read'),
    path('reserved_list', reserved_hole_detail_view, name="reserved_list"),
    path('search', HoleSearchView.as_view(), name="search"),
    path('<int:pk>/question/create',hole_question_register_view, name="question_create" ),
    path('<int:pk>/question/update/<int:question_id>',hole_question_update_view, name="question_update" ),
    path('<int:pk>/question/delete/<int:question_id>',hole_question_delete_view, name="question_delete" ),
    path('<int:pk>/questions',hole_question_allread_view, name="questions" ),
]
