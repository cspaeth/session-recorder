import os
import reapy
from os import mkdir
from shutil import copy
from os import path
from threading import RLock, Timer, Thread
from time import sleep
from django.conf import settings
from reapy.errors import DisabledDistAPIError

from ssr.store.util import StateModule
import logging
log = logging.getLogger(__name__)


DISCONNECTED = {
    'state': "disconnected"
}

CONNECTED = {
    'state': 'connected'
}


# noinspection PyPep8Naming
class reaper_access:
    API = RLock()

    def __init__(self, send_update=True):
        self.send_update = send_update

    def run_guarded(self, f, *args, **kwargs):
        with self.API:
            try:
                return f(*args, **kwargs)
            except (ConnectionError, DisabledDistAPIError) as e:
                log.error("Error connecting to reaper %s" % e)
                args[0].on_disconnect()
            finally:
                if self.send_update:
                    args[0].update_module_status()

    def __call__(self, f):
        def inner(*args, **kwargs):
            return self.run_guarded(f, *args, **kwargs)
        return inner


class ReaperRecorder(StateModule):

    def __init__(self):
        super().__init__()
        self.connected_once = False
        self.is_connected = False
        self.on_connect = None

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
            log.info("Connecting to reaper (address=%s)..." % settings.REAPER_IP)
            reapy.connect(settings.REAPER_IP)
            self.connected_once = True
            Thread(target=self.periodic_recorder_update, daemon=True).start()
        else:
            log.info("Reconnecting to reaper...")
            reapy.reconnect()

        self.is_connected = True
        log.info("Connected to reaper!")

        if self.on_connect:
            self.on_connect()

    @reaper_access()
    def start_new_project(self, name):
        session_file_host = self._create_project_from_template(name)
        self._open_project(session_file_host)
        return session_file_host

    @reaper_access()
    def open_project(self, session_file_host):
        self._open_project(session_file_host)

    @reaper_access()
    def close_project(self):
        self._save_current_project()
        reapy.Project().close()

    @reaper_access()
    def start_recording(self):
        project = reapy.Project()
        project.perform_action(40043)  # Go to end of project
        project.perform_action(41040)  # Go to next measure start
        project.perform_action(41040)  # ... again - to create a bit of space between takes

        start_position = project.cursor_position
        self._addGuideTrack(project, start_position)

        project.record()
        return start_position

    @reaper_access()
    def stop_recording(self):
        project = reapy.Project()
        project.stop()

        item = next((i for i in project.selected_items if i.track.name == "Console Mix"), None)
        if item:
            return item.length, item.active_take.source.filename

    @reaper_access()
    def stop(self):
        reapy.Project().stop()

    @reaper_access()
    def select(self, start, length):
        project = reapy.Project()
        project.time_selection = start, start + length
        project.perform_action(40630)  # go to start of selection

    @reaper_access()
    def add_take_marker(self, start, length, name):
        project = reapy.Project()
        project.add_region(start, start + length, name)

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

    @reaper_access(send_update=False)
    def get_module_status(self):
        if not self.is_connected:
            return DISCONNECTED

        # track_one = 57
        # track_step = 8
        # track_count = 20
        with reapy.inside_reaper():

            project = reapy.Project()
            if project.name == '':
                return CONNECTED

            # channels = []
            # for command in range(track_one, track_one + track_count * track_step, track_step):
            #     channels.append(reapy.reascript_api.GetToggleCommandState(command))
            #
            # # log.debug(channels)
            # levels = []
            # for track in range(track_count):
            #     track_id = project.tracks[track].id
            #     levels.append(reapy.reascript_api.Track_GetPeakHoldDB(track_id, 0, False))
            #     reapy.reascript_api.Track_GetPeakHoldDB(track_id, 0, True)
            # log.debug(levels)

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

    def _addGuideTrack(self, project, start_position):
        guide_dir = path.join(project.path, "guide")
        guide_dir_local = guide_dir.replace(settings.HOST_PATH, settings.BASE_PATH)
        if path.exists(guide_dir_local):
            candidates = [f for f in os.listdir(guide_dir_local) if f.endswith(".mp3")]
            if candidates:
                guide_track = path.join(guide_dir, candidates[0])
                project.selected_tracks = [project.tracks[0]]
                reapy.reascript_api.InsertMedia(guide_track, 0)
                project.cursor_position = start_position

    def _open_project(self, project_file):
        if self.get_open_project_path() != project_file:
            self._save_current_project()
            reapy.open_project(project_file)

    @staticmethod
    def _create_project_from_template(name):
        session_file = path.join(name, "session.RPP")
        mkdir(path.join(settings.BASE_PATH, name))
        copy(settings.BASE_TEMPLATE, path.join(settings.BASE_PATH, session_file))
        session_file_host = path.join(settings.HOST_PATH, session_file)
        return session_file_host
