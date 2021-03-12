from django.urls import include, path

from rest_framework.routers import DefaultRouter
from . import views

# router = DefaultRouter()
# router.register('session', views.sessionViewSet)

app_name = 'holes'
urlpatterns = [
    path('', views.HoleList.as_view()),
    path('<int:pk>/', views.HoleDetail.as_view())
]
# urlpatterns = [
#     path('', include(router.urls)),
# ]
# urlpatterns = [
#     path('', views.session_list),
# ]