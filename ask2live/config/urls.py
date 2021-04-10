"""ask2live URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .settings import production, development, base
from django.views.generic import TemplateView

schema_view = get_schema_view(
   openapi.Info(
      title="Ask2Live API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="skyhs1100@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

react_views_regex = r'\/|\b'.join([

    # List all your react routes here
    'main',
    'login',
    'createSession',
    'mypage',
    'session'

]) + r'\/'

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path( '', TemplateView.as_view(template_name='index.html'),name='index'),
    path('admin/', admin.site.urls),
    re_path(r'^$', TemplateView.as_view(template_name='index.html'),name='index'),
    re_path(react_views_regex, TemplateView.as_view(template_name='index.html')),
    # path('<path:route>',TemplateView.as_view(template_name='index.html'),name='index'),
    # re_path(r'^(%s)?$' % '|'.join(routes), TemplateView.as_view(template_name='index.html')),
    #REST FRAMEWORK URls
    path('chat/', include('chat_messages.urls')), # 테스트용 -- 삭제 필요
    path('api/hole/', include('holes.urls')),
    path('api/user/', include('users.urls', 'user_api')),
    path('api/reservation/', include('hole_reservations.urls')),
]

if production.DEBUG:
    urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)

if development.DEBUG:
    urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)