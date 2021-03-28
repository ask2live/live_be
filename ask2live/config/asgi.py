"""
ASGI config for ask2live project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django
# from django.core.asgi import get_asgi_application
from channels.routing import get_default_application
# from channels.asgi import get_channel_layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')


django.setup()
application = get_default_application()
# channel_layer = get_channel_layer()

