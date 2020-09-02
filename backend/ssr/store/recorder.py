from os import mkdir
from shutil import copy
from os import path
from threading import RLock, Timer, Thread
from time import sleep

import reapy
from django.conf import settings
from reapy.errors import DisabledDistAPIError

from ssr.store.util import StateModule
import logging
log = logging.getLogger(__name__)


DISCONNECTED = {
    'state': "disconnected"  # connected, ready, recording, playing,
}
CONNECTED = {
    'state': 'connected'
}


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
    name = 'RECORDER'

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
            log.warning("Connecting to reaper (adress=%s)..." % settings.REAPER_IP)
            reapy.connect(settings.REAPER_IP)
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
        mkdir(path.join(settings.BASE_PATH, name))
        copy(settings.BASE_TEMPLATE, path.join(settings.BASE_PATH, session_file))
        session_file_host = path.join(settings.HOST_PATH, session_file)
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
