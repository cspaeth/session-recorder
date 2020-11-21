import logging

from collections import OrderedDict
from django.conf import settings
from ssr.utils import send_to_group

log = logging.getLogger(__name__)


class ApplicationStore:
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

    def register_module(self, module, name):
        self.modules[name] = module
        self.state[name] = module.get_module_status()
        module.add_listener(lambda state: self.update(name, state))

    def update(self, module_name, data):
        # log.info("state update %s -> %s", module_name, data)
        self.state[module_name] = data
        send_to_group(settings.SESSION_GROUP_NAME, 'send_update', module_name)

    def dispatch_action(self, action_name, data):
        for module in self.modules.values():
            method = getattr(module, action_name, None)
            if method and getattr(method, 'isAction', False):
                method(data)


class StateModule:
    def __init__(self):
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def update_module_status(self):
        status = self.get_module_status()
        for listener in self._listeners:

            listener(status)

    def get_module_status(self):
        pass


def action(f):
    f.isAction = True
    return f
