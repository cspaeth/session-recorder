import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from ssr.store import STATUS
from ssr.store.auth import Authentication
from ssr.store.recorder import ReaperRecorder
from ssr.store.session import SessionRecorder

log = logging.getLogger(__name__)

reaper = ReaperRecorder()

recorder = SessionRecorder(reaper)
auth = Authentication()

STATUS.register_module(auth)
STATUS.register_module(recorder)
STATUS.register_module(reaper)


class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            settings.SESSION_ROOM_NAME,
            self.channel_name
        )

        for status in STATUS.all_states():
            self.send_json(status)

    def send_update(self, data):
        scope = data['scope']
        self.send_json(STATUS.get_status_message(scope))

    def receive_json(self, content, **kwargs):
        STATUS.dispatch_action(content['action'], content.get('data', None))
