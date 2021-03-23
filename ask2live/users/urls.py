from django.urls import path, include

from .views import registration_view, Logout, user_properties_view,user_update_view, ObtainAuthTokenView

# from rest_framework.authtoken.views import obtain_auth_token
app_name="user"
urlpatterns = [
    path('register', registration_view, name="register"),
    path('login', ObtainAuthTokenView.as_view(), name="login"), # login을 커스텀 뷰로 변경
    path('logout', Logout.as_view(), name="logout"),
    # path('read', read_view.as_view(), name='read'),
    path('read', user_properties_view, name='read'),
    path('update', user_update_view, name='update'),
]