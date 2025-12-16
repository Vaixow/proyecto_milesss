import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

import calificaciones.routing
from calificaciones.middleware import JwtAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miles_project.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(
        URLRouter(
            calificaciones.routing.websocket_urlpatterns
        )
    ),
})
