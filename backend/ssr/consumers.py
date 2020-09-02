import logging
from os import mkdir, path
from shutil import copy
from threading import Timer, RLock, Thread
from time import sleep

import reapy
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from reapy.errors import DisabledDistAPIError

from ssr.apps.models.models import Session, Take
import reapy.reascript_api


log = logging.getLogger(__name__)
SESSION_ROOM_NAME = 'session'

CURRENT_USER = "csp"

STATUS = {
    'auth': {
        'user': 'csp',
    },
}

API = RLock()

def reaper_access(f):
    def inner(*args, **kwargs):
        with API:
            log.debug("Reaper guarded: %s " % f.__name__)
            try:
                return f(*args, **kwargs)
            except (ConnectionError, DisabledDistAPIError):
                log.exception("Error connecting to recoder, trying to reconnect")
                args[0].on_disconnect()

    return inner


def mutation(name, data):
    return {
        'action': name,
        'data': data
    }

HOST_PATH = "/Users/csp/Projects/session-recorder/var/sessions/"
BASE_PATH = "/sessions/"
BASE_TEMPLATE = BASE_PATH + "template.RPP"
SESSION_FILE_NAME = "Session.RPP"
REAPER_IP = "192.168.178.32"

DISCONNECTED = {
    'state': "disconnected"  # connected, ready, recording, playing,
}
CONNECTED = {
    'state': 'connected'
}


class ApplicationState:
    def __init__(self):
        self.state = {
            'RECORDER_UPDATE': {},
            'UPDATE_FULL_SESSION': {}
        }

    def update(self, module, data):
        # log.info("state update %s -> %s", module, data)
        self.state[module] = data
        async_to_sync(get_channel_layer().group_send)(
            SESSION_ROOM_NAME,
            {
                'type': 'send_update',
                'scope': module
             }
        )


appState = ApplicationState()


class ReaperRecorder:
    def __init__(self):
        self.connected_once = False

    @reaper_access
    def connect(self):
        if not self.connected_once:
            log.warning("Connecting to reaper (adress=%s)..." % REAPER_IP)
            reapy.connect(REAPER_IP)
            self.connected_once = True
        else:
            log.warning("Reconnecting to reaper...")
            reapy.reconnect()

        log.info("Connected to reaper!")
        self.on_connect()

    @reaper_access
    def start_new_project(self, name):
        session_file_host = self._create_project_from_template(name)
        self.open_project(session_file_host)
        return session_file_host

    @reaper_access
    def open_project(self, project_file):
        if self.get_open_project_path() != project_file:
            self._save_current_project()
            reapy.open_project(project_file)

    @reaper_access
    def close_project(self):
        self._save_current_project()
        reapy.Project().close()

    @reaper_access
    def start_recording(self):
        project = reapy.Project()
        project.perform_action(40043)  # Go to end of project
        start_position = project.cursor_position
        project.perform_action(1013)  # Record
        return start_position

    @reaper_access
    def stop(self):
        project = reapy.Project()
        project.stop()
        return project.length

    @reaper_access
    def select(self, start, length):
        project = reapy.Project()
        project.time_selection = start, start + length
        project.perform_action(40630)  # go to start of selection

    @reaper_access
    def seek(self, position):
        reapy.Project().cursor_position = position

    @reaper_access
    def play(self):
        reapy.Project().play()

    @reaper_access
    def get_open_project_path(self):
        project = reapy.Project()
        return path.join(project.path, project.name)

    @reaper_access
    def _save_current_project(self):
        current_project = reapy.Project()
        if current_project.is_dirty:
            current_project.save()

    def _create_project_from_template(self, name):
        session_file = path.join(name, "%s.RPP" % name)
        mkdir(path.join(BASE_PATH, name))
        copy(BASE_TEMPLATE, path.join(BASE_PATH, session_file))
        session_file_host = path.join(HOST_PATH, session_file)
        return session_file_host

    @reaper_access
    def get_status(self):
        project = reapy.Project()
        if project.name == '':
            return CONNECTED

        state = 'ready'
        position = 0
        if project.is_recording:
            state = 'recording'
            position = project.play_position - project.cursor_position
        elif project.is_playing:
            state = 'playing'
            position = project.play_position - project.time_selection.start

        return {
            'position': position,
            'state': state
        }


reaper = ReaperRecorder()



def with_session(f):
    def inner(self, *args, **kwargs):
        session = Session.objects.filter(pk=self.session_id).first()
        if session and self.reaper.get_open_project_path() == session.project_file:
            args = args + (session,)
            result = f(self, *args, **kwargs)
            appState.update('UPDATE_FULL_SESSION', session.to_dict())
            return result
        else:
            log.warning("No active session, did not execute %s" % f.__name__)
    return inner



class SessionRecorder():
    def __init__(self):
        self.reaper = reaper
        self.session_id = None
        self.recorder_state = DISCONNECTED

        reaper.on_connect = self.on_reaper_connected
        reaper.on_disconnect = self.on_reaper_disconnected
        reaper.connect()

        timer = Thread(target=self.scheduled_recorder_update)
        timer.setDaemon(True)
        timer.start()

    def scheduled_recorder_update(self):
        while True:
            sleep(.1)
            if self.recorder_state != DISCONNECTED:
                self._send_update(recorder=True, session=False)

    def on_reaper_connected(self):
        log.warning("Reaper connected-   - - - - - - - - -")
        self.recorder_state = CONNECTED
        self._identfy_open_project()

    def on_reaper_disconnected(self):
        log.warning("Reaper was disconnected, will try to reconnect soon")
        self.session_id = None
        self.recorder_state = DISCONNECTED
        timer = Timer(10, reaper.connect)
        timer.setDaemon(True)
        timer.start()

        self._send_update(session=False)

    def session_start(self, session_name):
        session_file_location = reaper.start_new_project(session_name)
        self._create_session(session_name, session_file_location)
        self._send_update(recorder=True)

    @with_session
    def session_close(self, data, session):
        reaper.close_project()
        self.session_id = None
        self.recorder_state = CONNECTED
        self._send_update(recorder=True)

    @with_session
    def set_next_take_name(self, take_name, session):
        session.next_take_name = take_name
        session.save()
        self._send_update()

    @with_session
    def take_start(self, data, session):
        start_position = reaper.start_recording()
        self._create_take(session, start_position)
        self._send_update(recorder=True)

    @with_session
    def take_stop(self, data, session):
        end_position = reaper.stop()
        session.active_take.length = end_position - session.active_take.location
        session.active_take.save()
        reaper.select(session.active_take.location, session.active_take.length)
        self._send_update(recorder=True)


    @with_session
    def take_select(self, number, session):
        take = session.takes.filter(number=number).first()
        reaper.select(take.location, take.length)
        session.active_take = take
        session.save()
        self._send_update(recorder=True)

    @with_session
    def take_seek(self, position, session):
        reaper.seek(session.active_take.location + position)
        self._send_update(session=False, recorder=True)

    @with_session
    def play(self, *args):
        reaper.play()
        self._send_update(recorder=True)

    @with_session
    def stop(self, *args):
        reaper.stop()
        self._send_update(recorder=True)

    def _send_update(self, session=True, recorder=False):
        if recorder:
            self.recorder_state = reaper.get_status()
            appState.update('RECORDER_UPDATE', self.recorder_state)

    def _create_take(self, session, position):
        take = session.takes.create(number=session.next_take_number,
                                    name=session.next_take_name,
                                    location=position)
        self.current_take_number = take.number
        session.next_take_number += 1
        session.active_take = take
        session.save()

    def _create_session(self, name, session_file_host):
        session = Session.objects.create(name=name, username=CURRENT_USER,
                                         project_file=session_file_host)

        self.session_id = session.id

    def _identfy_open_project(self):
        log.warning("Identigy open Project")
        session_file = reaper.get_open_project_path()

        session = Session.objects.filter(project_file=session_file).first()
        if session:
            appState.update('UPDATE_FULL_SESSION', session.to_dict())
            self.session_id = session.id


recorder = SessionRecorder()



class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            SESSION_ROOM_NAME,
            self.channel_name
        )

        self.send_json(mutation('ACTIVE_USER', CURRENT_USER))

        self.send_update({'scope': 'UPDATE_FULL_SESSION'})
        self.send_update({'scope': 'RECORDER_UPDATE'})

    def send_update(self, data):
        scope = data['scope']
        self.send_json(mutation(scope, appState.state[scope]))

    def receive_json(self, content, **kwargs):
        getattr(recorder, content['action'])(content.get('data', None))

# login / logout
# session_start / session_close
# take_start / take_stop / take_cancel / take_select / take_play / take_seek
# take_next_name


