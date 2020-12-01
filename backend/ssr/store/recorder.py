import os
import reapy
from os import mkdir
from shutil import copy
from os import path
from threading import RLock, Timer, Thread
from time import sleep
from django.conf import settings
from reapy.errors import DisabledDistAPIError

from ssr.store.util import StateModule, action
import logging
log = logging.getLogger(__name__)


DISCONNECTED = {
    'state': "disconnected"
}

CONNECTED = {
    'state': 'connected'
}

GUIDE_TRACK = 0
CONSOLE_MIX_TRACK = 1
FIRST_RAW_TRACK = 3
RAW_TRACK_COUNT = 24
ACTION_TOGGLE_CHANNEL_1 = 25
COMMANDS_PER_CHANNEL = 8

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
            sleep(.2)
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
    def start_recording(self, tempo=None):
        project = reapy.Project()
        project.perform_action(40043)  # Go to end of project
        project.perform_action(41040)  # ... again - to create a bit of space between takes

        if tempo:
            log.debug("Setting Tempo to %i" % tempo)
            reapy.reascript_api.SetTempoTimeSigMarker(0, -1, project.cursor_position, -1, -1, tempo, 0, 0, 0)

        start_position = project.cursor_position
        self._addGuideTrack(project, start_position)

        project.record()
        return start_position

    @reaper_access()
    def stop_recording(self):
        project = reapy.Project()
        project.stop()

        item = next((i for i in project.selected_items if i.track.index == CONSOLE_MIX_TRACK), None)
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

    @action
    @reaper_access()
    def set_metronome_state(self, enable):
        metronome_action = enable and 41745 or 41746
        project = reapy.Project()
        project.perform_action(metronome_action)

    @action
    @reaper_access()
    @reapy.inside_reaper()
    def set_track_armed(self, data):
        track_number, record = data
        project = reapy.Project()
        track = project.tracks[FIRST_RAW_TRACK + track_number]
        reapy.reascript_api.SetMediaTrackInfo_Value(track.id, 'I_RECARM', record)

    @reaper_access(send_update=False)
    def get_module_status(self):
        if not self.is_connected:
            return DISCONNECTED

        with reapy.inside_reaper():
            project = reapy.Project()
            if project.name == '':
                return CONNECTED

            channels = []
            # levels = []
            for i in range(RAW_TRACK_COUNT):
                command = ACTION_TOGGLE_CHANNEL_1 + (FIRST_RAW_TRACK + i) * COMMANDS_PER_CHANNEL
                channels.append(reapy.reascript_api.GetToggleCommandState(command))

                # track_id = project.tracks[i + FIRST_RAW_TRACK].id
                # levels.append(reapy.reascript_api.Track_GetPeakHoldDB(track_id, 0, False))
                # reapy.reascript_api.Track_GetPeakHoldDB(track_id, 0, True)

            metronome = reapy.reascript_api.GetToggleCommandState(40364)

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
            'state': state,
            'channels': channels,
            # 'levels': levels,
            'metronome': metronome
        }

    def _addGuideTrack(self, project, start_position):
        guide_dir = path.join(project.path, "guide")
        guide_dir_local = guide_dir.replace(settings.HOST_PATH, settings.BASE_PATH)
        if path.exists(guide_dir_local):
            candidates = [f for f in os.listdir(guide_dir_local) if f.endswith(".mp3")]
            if candidates:
                guide_track = path.join(guide_dir, candidates[0])
                project.selected_tracks = [project.tracks[GUIDE_TRACK]]
                project.perform_action(41040)  # Jump two measures forward, insert item
                project.perform_action(41040)
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
