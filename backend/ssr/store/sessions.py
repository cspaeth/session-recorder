

from ssr.apps.models.models import Session
from ssr.store.util import StateModule
import logging

log = logging.getLogger(__name__)


class SessionArchive(StateModule):
    def __init__(self, auth):
        super().__init__()
        self.current_user = ""
        auth.add_listener(self.auth_changed)

    def auth_changed(self, status):
        self.current_user = status
        self.update_module_status()

    def get_module_status(self):
        if not self.current_user:
            log.info("sending [] sessions")
            return []
        my_sessions = Session.objects.filter(username=self.current_user)
        result = [{
            'id': s.id,
            'name': s.name
        } for s in my_sessions]
        log.info("sending sessions")
        return result
