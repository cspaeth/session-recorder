import logging

from ssr.apps.models.models import Session
from ssr.store.auth import CURRENT_USER
from ssr.store.util import StateModule, action

log = logging.getLogger(__name__)


def with_session(f):
    def inner(self, *args, **kwargs):

        session = Session.objects.filter(pk=self.session_id).first()
        if session:
            args = args + (session,)
            result = f(self, *args, **kwargs)
            self.update_module_status()
            return result
        else:
            log.warning("No active session, did not execute %s" % f.__name__)

    return inner


# noinspection PyUnusedLocal
class SessionControl(StateModule):

    def __init__(self, reaper):
        super().__init__()
        self.reaper = reaper
        self.session_id = None
        self.reaper.on_connect = self.on_reaper_connected
        self.reaper.connect()

    def on_reaper_connected(self):
        log.warning("Reaper connected-   - - - - - - - - -")
        self._identify_open_project()

    def get_module_status(self):
        session = Session.objects.filter(pk=self.session_id).first()
        if session:
            return session.to_dict()

    @action
    def session_start(self, session_name):
        session_file_location = self.reaper.start_new_project(session_name)
        session = Session.objects.create(name=session_name, username=CURRENT_USER,
                                         project_file=session_file_location)
        self.session_id = session.id
        self.update_module_status()

    @action
    @with_session
    def session_close(self, *args):
        self.reaper.close_project()
        self.session_id = None

    @action
    @with_session
    def set_next_take_name(self, take_name, session):
        session.next_take_name = take_name
        session.save()

    @action
    @with_session
    def take_start(self, data, session):
        start_position = self.reaper.start_recording()
        self._create_take(session, start_position)

    @action
    @with_session
    def take_stop(self, data, session):
        end_position = self.reaper.stop()
        session.active_take.length = end_position - session.active_take.location
        session.active_take.save()
        self.reaper.select(session.active_take.location, session.active_take.length)

    @action
    @with_session
    def take_select(self, number, session):
        take = session.takes.filter(number=number).first()
        self.reaper.select(take.location, take.length)
        session.active_take = take
        session.save()

    @action
    @with_session
    def take_seek(self, position, session):
        self.reaper.seek(session.active_take.location + position)

    @action
    @with_session
    def play(self, *args):
        self.reaper.play()

    @action
    @with_session
    def stop(self, *args):
        self.reaper.stop()

    def _create_take(self, session, position):
        take = session.takes.create(number=session.next_take_number,
                                    name=session.next_take_name,
                                    location=position)
        self.current_take_number = take.number
        session.next_take_number += 1
        session.active_take = take
        session.save()

    def _identify_open_project(self):
        log.warning("Identify open Project")
        session_file = self.reaper.get_open_project_path()

        session = Session.objects.filter(project_file=session_file).first()
        if session:
            self.session_id = session.id
            self.update_module_status()
