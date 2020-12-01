import logging
from threading import Thread

from ssr.apps.models.models import Session
from ssr.processing import UploadProcessor
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

    def __init__(self, reaper, auth):
        super().__init__()
        self.reaper = reaper
        self.auth = auth
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
        session_file_location = self.reaper.start_new_project("%s/%s" % (self.auth.current_user, session_name))
        session = Session.objects.create(name=session_name, username=self.auth.current_user,
                                         project_file=session_file_location)
        self.session_id = session.id
        self.update_module_status()

    @action
    def session_open(self, session_id):
        if self.auth.current_user:
            session = Session.objects.get(pk=int(session_id))
            self.reaper.open_project(session.project_file)
            self.session_id = session.id
        self.update_module_status()

    @action
    @with_session
    def session_close(self, *args):
        self.reaper.close_project()
        self.session_id = None

    @action
    @with_session
    def session_upload(self, data, session):
        processor = UploadProcessor()
        Thread(processor.upload_session(self.session_id, self.update_module_status)).start()

    @action
    @with_session
    def set_next_take_name(self, take_name, session):
        session.next_take_name = take_name
        session.save()

    @action
    @with_session
    def set_next_take_tempo(self, tempo, session):
        session.next_take_tempo = tempo
        session.save()

    @action
    @with_session
    def take_queue(self, take_number, session):
        take = session.takes.filter(number=take_number).first()
        take.queue()
        take.save()

    @action
    @with_session
    def take_unqueue(self, take_number, session):
        take = session.takes.filter(number=take_number).first()
        take.unqueue()
        take.save()

    @action
    @with_session
    def take_start(self, data, session):
        start_position = self.reaper.start_recording(session.next_take_tempo)
        self._create_take(session, start_position)

    @action
    @with_session
    def take_stop(self, data, session):
        (length, filename) = self.reaper.stop_recording()
        active_take = session.active_take
        active_take.take_mix_source = filename
        active_take.length = length
        active_take.stop()
        active_take.save()
        self.reaper.select(active_take.location, active_take.length)
        self.reaper.add_take_marker(active_take.location, active_take.length,
                                    "Take %s - %s" % (active_take.number, active_take.name))

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
