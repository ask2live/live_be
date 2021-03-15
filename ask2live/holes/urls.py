from django.urls import include, path

from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    hole_create_view,
    hole_detail_view,
    hole_update_view,
    hole_delete_view,
)


# router = DefaultRouter()
# router.register('session', views.sessionViewSet)

app_name = 'holes'
# urlpatterns = [
#     path('', views.HoleList.as_view()),
#     path('<int:pk>/', views.HoleDetail.as_view())
# ]
urlpatterns = [
    path('', hole_detail_view, name="detail"),
    path('create/', hole_create_view, name="create"),
    path('<int:pk>/update/', hole_update_view, name="update"),
    path('<int:pk>/delete/', hole_delete_view, name="delete"),
]
# urlpatterns = [
#     path('', views.session_list),
# ]