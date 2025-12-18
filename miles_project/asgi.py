import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import calificaciones.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miles_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            calificaciones.routing.websocket_urlpatterns
        )
    ),
})
