import logging
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings
from ssr.store import store

log = logging.getLogger(__name__)


class RemoteConsumer(JsonWebsocketConsumer):
    groups = [settings.SESSION_GROUP_NAME, settings.MIXER_GROUP_NAME]

    def connect(self):
        log.info("Client Connected")
        self.accept()
        self.send_initial()


    def osc_input(self, data):
        # print("Sending to ws Client: %s" % str(data['data']))
        self.send_json({
            'action': "MIXER_OSC_INPUT",
            'data': data['data']
        })

    def send_initial(self):
        for status in store.all_states():
            self.send_json(status)

    def session_update(self, data):
        store.modules['SESSION'].update_module_status()

    def send_update(self, data):
        self.send_json(store.get_status_message(data['data']))

    def receive_json(self, content, **kwargs):
        # print("Recived from WS")
        store.dispatch_action(content['action'], content.get('data', None))
