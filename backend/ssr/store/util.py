import logging
from collections import OrderedDict
from functools import wraps
from time import time

log = logging.getLogger(__name__)


class ApplicationStore:
    def __init__(self):
        self.modules = OrderedDict()
        self.state = {}

    def get_status_message(self, module_name):
        return {
            'action': module_name,
            'data': self.modules[module_name].get_module_status()
        }

    def register_module(self, module):
        self.modules[module.name] = module

    def dispatch_action(self, action_name, data):
        for module in self.modules.values():
            method = getattr(module, action_name, None)
            if method and getattr(method, 'isAction', False):
                method(data)


def action(f):
    f.isAction = True
    return f


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return wrap
