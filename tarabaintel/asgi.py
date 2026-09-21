import os

# 1. Set the settings module FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarabaintel.settings')

# 2. Initialize Django application (this calls django.setup() and loads all apps)
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 3. NOW it is 100% safe to import Channels and our routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from insight.routing import websocket_urlpatterns

# 4. Combine them
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
