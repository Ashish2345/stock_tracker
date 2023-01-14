import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from notification.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            
            )
        )
    }
)

#AuthMiddlewareStack= self.scope for request.user 