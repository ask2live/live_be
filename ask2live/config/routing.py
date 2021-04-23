from django.conf.urls import url
from django.urls import re_path,path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from chat_messages.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/hole/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer1.as_asgi()) # 테스트용
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
            URLRouter(        
                    websocket_urlpatterns
            )
        )
})
