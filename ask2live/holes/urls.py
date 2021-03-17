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
)


# router = DefaultRouter()
# router.register('session', views.sessionViewSet)

app_name = 'holes'

urlpatterns = [
    path('', hole_detail_view, name="detail"),
    path('create', hole_create_view, name="create"),
    path('update/<int:hole_id>', hole_update_view, name="update"),
    path('delete/<int:hole_id>', hole_delete_view, name="delete"),
    path('reserved_list', reserved_hole_detail_view, name="reserved_list"),
    path('search', HoleSearchView.as_view(), name="search"),
]
