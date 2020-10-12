from django.conf import settings
from ssr.store.util import StateModule, action
from os import path, mkdir
import logging

log = logging.getLogger(__name__)


class Authentication(StateModule):
    current_user = None

    def get_module_status(self):
        return self.current_user

    @action
    def login(self, data):
        self.ensure_userdir_exists(data['username'])
        self.current_user = data['username']
        self.update_module_status()

    @action
    def logout(self, *args):
        self.current_user = None
        self.update_module_status()

    def ensure_userdir_exists(self, username):
        user_dir = path.join(settings.BASE_PATH, username)
        if not path.exists(user_dir):
            log.info("Creating user dir: %s" % user_dir)
            mkdir(user_dir)


