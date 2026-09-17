import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from insight.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarabaintel.settings')

application = ProtocolTypeRouter({
    # Handles normal HTTP requests (Web pages, API)
    "http": get_asgi_application(),
    
    # Handles WebSocket connections (Real-time Map)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
