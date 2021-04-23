from django.test import TestCase
import asyncio
from urllib.parse import unquote

import pytest
from django.urls import path

from channels.consumer import AsyncConsumer
from channels.generic.websocket import WebsocketConsumer
from channels.routing import URLRouter
from channels.testing import HttpCommunicator, WebsocketCommunicator

# from channels.tests.test_testing import SimpleWebsocketApp

# Create your tests here.
class MyTests(TestCase):
    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_websocket_application(self):
        """
        Tests that the WebSocket communicator class works with the
        URLRoute application.
        """
        application = URLRouter([path("testws/<str:message>/", KwargsWebSocketApp)])
        # application = URLRouter([
        # path(r"^testws/(?P<message>\w+)/$", KwargsWebSocketApp()),
        # ])
        communicator = WebsocketCommunicator(application, "/testws/test/")
        connected, subprotocol = await communicator.connect()
        # Test connection
        assert connected
        assert subprotocol is None
        message = await communicator.receive_from()
        assert message == "test"
        await communicator.disconnect()

class SimpleWebsocketApp(WebsocketConsumer):

    def connect(self):
        assert self.scope["path"] == "/testws/"
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=text_data, bytes_data=bytes_data)

class KwargsWebSocketApp(WebsocketConsumer):
    """
    WebSocket ASGI app used for testing the kwargs arguments in the url_route.
    """
    def connect(self):
        self.accept()
        self.send(text_data=self.scope["url_route"]["kwargs"]["message"])
    
class ConnectionScopeValidator(WebsocketConsumer):
    """
    Tests ASGI specification for the connection scope.
    """

    def connect(self):
        assert self.scope["type"] == "websocket"
        # check if path is a unicode string
        assert isinstance(self.scope["path"], str)
        # check if path has percent escapes decoded
        assert self.scope["path"] == unquote(self.scope["path"])
        # check if query_string is a bytes sequence
        assert isinstance(self.scope["query_string"], bytes)
        self.accept()