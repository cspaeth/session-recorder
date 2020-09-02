import logging
from collections import OrderedDict
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
HOST_PATH = "/Users/csp/Projects/session-recorder/var/sessions/"
BASE_PATH = "/sessions/"
BASE_TEMPLATE = BASE_PATH + "template.RPP"
SESSION_FILE_NAME = "Session.RPP"
REAPER_IP = "192.168.178.32"
CURRENT_USER="Chriss"
DISCONNECTED = {
    'state': "disconnected"  # connected, ready, recording, playing,
}
CONNECTED = {
    'state': 'connected'
}


class ApplicationState:
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

    def register_module(self, module):
        print (module.name)
        self.modules[module.name] = module
        self.state[module.name] = module.get_module_status()

    def update(self, module_name, data):
        # log.info("state update %s -> %s", module, data)
        self.state[module_name] = data
        async_to_sync(get_channel_layer().group_send)(
            SESSION_ROOM_NAME,
            {
                'type': 'send_update',
                'scope': module_name
             }
        )

    def dispatch_action(self, action_name, data):
        for module in self.modules.values():
            method = getattr(module, action_name, None)
            if method and getattr(method, 'isAction', False):
                method(data)


class StateModule:
    name = None

    def update_module_status(self):
        appState.update(self.name, self.get_module_status())


def action(f):
    f.isAction = True
    return f


class reaper_access:
    API = RLock()

    def __init__(self, send_update=True):
        self.send_update = send_update

    def __call__(self, f):
        def inner(*args, **kwargs):
            with self.API:
                log.debug("Reaper guarded: %s " % f.__name__)
                try:
                    return f(*args, **kwargs)
                except (ConnectionError, DisabledDistAPIError):
                    log.exception("Error connecting to recoder, trying to reconnect")
                    args[0].on_disconnect()
                finally:
                    if self.send_update:
                        args[0].update_module_status()
        return inner


class ReaperRecorder(StateModule):

    name = 'RECORDER_UPDATE'
    def __init__(self):
        self.connected_once = False
        self.is_connected = False

    def periodic_recorder_update(self):
        while True:
            sleep(.1)
            self.update_module_status()

    def on_disconnect(self):
        self.is_connected = False
        self.update_module_status()
        log.warning("Disconnected - scheduling reconnect in 10 s")
        timer = Timer(10, self.connect)
        timer.setDaemon(True)
        timer.start()

    @reaper_access()
    def connect(self):
        if not self.connected_once:
            log.warning("Connecting to reaper (adress=%s)..." % REAPER_IP)
            reapy.connect(REAPER_IP)
            self.connected_once = True
            Thread(target=self.periodic_recorder_update, daemon=True).start()
        else:
            log.warning("Reconnecting to reaper...")
            reapy.reconnect()

        self.is_connected = True
        log.info("Connected to reaper!")
        self.on_connect()

    @reaper_access()
    def start_new_project(self, name):
        session_file_host = self._create_project_from_template(name)
        self._open_project(session_file_host)
        return session_file_host

    @reaper_access()
    def close_project(self):
        self._save_current_project()
        reapy.Project().close()

    @reaper_access()
    def start_recording(self):
        project = reapy.Project()
        project.perform_action(40043)  # Go to end of project
        start_position = project.cursor_position
        project.perform_action(1013)  # Record
        return start_position

    @reaper_access()
    def stop(self):
        project = reapy.Project()
        project.stop()
        return project.length

    @reaper_access()
    def select(self, start, length):
        project = reapy.Project()
        project.time_selection = start, start + length
        project.perform_action(40630)  # go to start of selection

    @reaper_access()
    def seek(self, position):
        reapy.Project().cursor_position = position

    @reaper_access()
    def play(self):
        reapy.Project().play()

    @reaper_access(send_update=False)
    def get_open_project_path(self):
        project = reapy.Project()
        return path.join(project.path, project.name)

    @reaper_access(send_update=False)
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

    @reaper_access(send_update=False)
    def get_module_status(self):
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

    def _open_project(self, project_file):
        if self.get_open_project_path() != project_file:
            self._save_current_project()
            reapy.open_project(project_file)



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


class SessionRecorder(StateModule):
    name = 'UPDATE_FULL_SESSION'

    def __init__(self, reaper):
        self.reaper = reaper
        self.session_id = None
        self.reaper.on_connect = self.on_reaper_connected
        self.reaper.connect()

    def on_reaper_connected(self):
        log.warning("Reaper connected-   - - - - - - - - -")
        self._identfy_open_project()

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
    def session_close(self, data, session):
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

    def _identfy_open_project(self):
        log.warning("Identigy open Project")
        session_file = self.reaper.get_open_project_path()

        session = Session.objects.filter(project_file=session_file).first()
        if session:
            self.session_id = session.id
            self.update_module_status()





class Authentication(StateModule):
    name = 'ACTIVE_USER'

    def get_module_status(self):
        return CURRENT_USER


appState = ApplicationState()
reaper = ReaperRecorder()

recorder = SessionRecorder(reaper)
auth = Authentication()

appState.register_module(auth)
appState.register_module(recorder)
appState.register_module(reaper)


class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            SESSION_ROOM_NAME,
            self.channel_name
        )

        for status in appState.all_states():
            self.send_json(status)

    def send_update(self, data):
        scope = data['scope']
        self.send_json(appState.get_status_message(scope))

    def receive_json(self, content, **kwargs):
        appState.dispatch_action(content['action'], content.get('data', None))


# login / logout
# session_start / session_close
# take_start / take_stop / take_cancel / take_select / take_play / take_seek
# take_next_name


