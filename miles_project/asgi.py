import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miles_project.settings")

# 👉 Primero se inicializa Django
django_asgi_app = get_asgi_application()

# 👉 Recién después se importa Channels
from channels.routing import ProtocolTypeRouter, URLRouter
from calificaciones.routing import websocket_urlpatterns
from calificaciones.middleware import JwtAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
