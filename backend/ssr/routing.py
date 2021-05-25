from django.urls import re_path
from . import consumers
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
    re_path(r'ws/remote/$', consumers.RemoteConsumer.as_asgi()),
    # re_path(r'ws/recorder/$', consumers.RecorderConsumer),
]


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
