from ssr.store.util import StateModule


CURRENT_USER="Chriss"


class Authentication(StateModule):
    name = 'ACTIVE_USER'

    def get_module_status(self):
        return CURRENT_USER
