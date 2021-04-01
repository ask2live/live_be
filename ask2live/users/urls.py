from django.urls import path, include

from .views import (
        registration_or_login_view,
        Logout, 
        user_properties_view,
        user_update_view, 
        ChangePasswordView,
        all_user_properties_view,
        user_follow_view,
        user_unfollow_view
        )
# from rest_framework.authtoken.views import obtain_auth_token
app_name="user"
urlpatterns = [
    path('login', registration_or_login_view, name="login"),
    # path('login', ObtainAuthTokenView.as_view(), name="login"), # login을 커스텀 뷰로 변경
    path('logout', Logout.as_view(), name="logout"),
    path('read', user_properties_view, name='read'),
    path('read/hole', user_properties_view, name='read_hole'),
    path('all_read', all_user_properties_view, name='all_read'),
    path('update', user_update_view, name='update'),
    path('follow/<int:user_id>', user_follow_view, name='follow'),
    path('unfollow/<int:user_id>', user_unfollow_view, name='unfollow'),
    path('change_password/', ChangePasswordView.as_view(), name="change_password"),
]