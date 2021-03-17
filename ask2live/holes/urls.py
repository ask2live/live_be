from django.urls import include, path

from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    hole_create_view,
    hole_detail_view,
    hole_update_view,
    hole_delete_view,
    MypageHoleView,
    reserved_hole_detail_view,
    live_hole_update_view,
    live_hole_create_view
)
app_name = 'holes'

urlpatterns = [
    path('', hole_detail_view, name="detail"),
    path('create', hole_create_view, name="create"),
    path('update/<int:pk>', hole_update_view, name="update"),
    path('delete/<int:pk>', hole_delete_view, name="delete"),
    path('list', MypageHoleView.as_view(), name="list"),
    path('reserved_list', reserved_hole_detail_view, name="reserved_list"),
    path('<int:pk>/live_update/<str:room_num>', live_hole_update_view, name="live/update"),
    path('<int:pk>/live_create', live_hole_create_view, name='live/create')
]
