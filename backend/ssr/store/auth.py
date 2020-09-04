from ssr.store.util import StateModule


CURRENT_USER = "Chriss"


class Authentication(StateModule):

    def get_module_status(self):
        return CURRENT_USER
