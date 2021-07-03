import logging
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings
from ssr.store import store

log = logging.getLogger(__name__)


class RemoteConsumer(JsonWebsocketConsumer):
    groups = [settings.MIXER_GROUP_NAME]

    def connect(self):
        log.info("Client Connected")
        self.accept()
        self.send_initial()

    def osc_input(self, message):
        log.debug("Received osc_input, forwarding to ws: %s" % str(message['data']))
        self.send_json({
            'action': "MIXER_OSC_INPUT",
            'data': message['data']
        })
        log.debug("... forwarded")

    def send_initial(self):
        log.info("Sending initial state to ws")
        for module_name in store.modules.keys():
            self.send_json(store.get_status_message(module_name))

    def send_update(self, message):
        self.send_json(store.get_status_message(message['data']))

    def receive_json(self, content, **kwargs):
        log.debug("Received from ws, about to dispatch: %s" % content)
        store.dispatch_action(content['action'], content.get('data', None))
        log.debug("... dispatched")
