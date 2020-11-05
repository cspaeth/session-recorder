from django.urls import re_path

from . import processing
from . import consumers
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

websocket_urlpatterns = [
    re_path(r'ws/remote/$', consumers.RemoteConsumer),
    # re_path(r'ws/recorder/$', consumers.RecorderConsumer),
]


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
    "channel": ChannelNameRouter({
        "processuploads": processing.UploadProcessor,
    }),
})
