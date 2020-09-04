import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from ssr.store import store

log = logging.getLogger(__name__)


class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        self.send_initial()
        async_to_sync(self.channel_layer.group_add)(
            settings.SESSION_ROOM_NAME,
            self.channel_name
        )

    def send_initial(self):
        for status in store.all_states():
            self.send_json(status)

    def send_update(self, data):
        self.send_json(store.get_status_message(data['scope']))

    def receive_json(self, content, **kwargs):
        store.dispatch_action(content['action'], content.get('data', None))
