from ssr.store.util import ApplicationStore
from ssr.store.x32 import X32Module

store = ApplicationStore()

x32 = X32Module()

store.register_module(x32)