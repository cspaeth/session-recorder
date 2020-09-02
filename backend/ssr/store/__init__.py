from collections import OrderedDict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings


class ApplicationState:
    def __init__(self):
        self.modules = OrderedDict()
        self.state = {}

    def all_states(self):
        return [self.get_status_message(module) for module in self.modules.keys()]

    def get_status_message(self, module_name):
        return {
            'action': module_name,
            'data': self.state[module_name]
        }

    def register_module(self, module):
        self.modules[module.name] = module
        self.state[module.name] = module.get_module_status()

    def update(self, module_name, data):
        # log.info("state update %s -> %s", module, data)
        self.state[module_name] = data
        async_to_sync(get_channel_layer().group_send)(
            settings.SESSION_ROOM_NAME,
            {
                'type': 'send_update',
                'scope': module_name
            }
        )

    def dispatch_action(self, action_name, data):
        for module in self.modules.values():
            method = getattr(module, action_name, None)
            if method and getattr(method, 'isAction', False):
                method(data)


STATUS = ApplicationState()