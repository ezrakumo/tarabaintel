from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/intelligence/$', consumers.IntelligenceConsumer.as_asgi()),
]
