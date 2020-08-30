import logging
from os import mkdir, path

from shutil import copy
from threading import Thread, Lock, Timer
from time import sleep

import reapy
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from reapy.tools._inside_reaper import inside_reaper

from ssr.apps.models.models import Session, Take
import reapy.reascript_api


log = logging.getLogger(__name__)
SESSION_ROOM_NAME = 'session'

CURRENT_USER = "csp"

STATUS = {
    'auth': {
        'user': 'csp',
    },
    'session': {
        'name': '123',
        'next_take': {
            'number': 1,
            'name': 'Song 4',
        },
        'takes': [
        ],
        'recorder':  {
            'state': 'connected',
            'current_take': 1,
            'current_session': None,
            'position': 0
        }
    },
}

RECORDER = {
    'CHANNEL_NAME': None
}

API = Lock()


def reconnect_on_error(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (ConnectionError, BrokenPipeError):
            log.exception("Error connecting to recoder, trying to reconnect")
            args[0].reconnect()

    return inner


def reaper_access(f):
    def inner(*args, **kwargs):
        with API:
            print(f.__name__)
            result = reconnect_on_error(f(*args, **kwargs))
            return result
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

DISCONNECTED = {
    'state': "disconnected"  # connected, ready, recording, playing,
}
CONNECTED = {
    'state': 'connected'
}


class ReaperRecorder:
    def __init__(self):
        self.status = DISCONNECTED
        self.current_take = None
        self.session_id = None

        self.reconnect_timer = None
        self.first_attempt = True

    def update_cycle(self):
        self.update_status()
        Timer(.1, self.update_cycle).start()

    def reconnect(self):
        log.warning("Reconnect")
        if not self.reconnect_timer:
            log.warning("Reconnectstate ")
            self.reconnect_timer = Timer(5.0, self.connect)
            self.reconnect_timer.start()


    @reaper_access
    def connect(self):
        self.reconnect_timer = None

        if self.first_attempt:
            reapy.connect("192.168.178.32")
            self.first_attempt = False
            Timer(.5, self.update_cycle).start()
        else:
            reapy.reconnect()

        self.status = CONNECTED
        self.current_take = None
        self.session_id = None

        project = reapy.Project()
        file = path.join(project.path, project.name)
        session = Session.objects.filter(project_file=file).first()
        if session:
            self.session_id = session.id
            self.send_session_update()
        self._update_status()


    @reaper_access
    def start_session(self, name):
        session_file = path.join(name, "Session.RPP")
        mkdir(path.join(BASE_PATH, name))
        copy(BASE_TEMPLATE, path.join(BASE_PATH, session_file))
        session_file_host = path.join(HOST_PATH, session_file)

        session = Session.objects.create(name=name, username=CURRENT_USER,
                                         project_file=session_file_host)

        current_project = reapy.Project()
        if current_project.is_dirty:
            current_project.save()

        reapy.open_project(session_file_host)

        self.session_id = session.id
        self.current_take = None

        self.send_session_update()
        self._update_status()



    @reaper_access
    def start_take(self):
        session = Session.objects.get(pk=self.session_id)
        project = reapy.Project()
        project.perform_action(40043)  # Go to end of project

        take = Take.objects.create(session=session,
                                   number=session.next_take_number,
                                   name=session.next_take_name,
                                   location=project.cursor_position)

        self.current_take = take.number
        session.next_take_number += 1
        session.save()

        project.perform_action(1013)  # Record
        self.send_session_update()
        self._update_status()


    @reaper_access
    def stop_take(self):
        project = reapy.Project()
        was_recording = project.is_recording
        project.stop()

        if was_recording:
            take = Take.objects.get(session=self.session_id, number=self.current_take)
            take.length = project.play_position - take.location
            take.save()
            project.time_selection = take.location, take.location + take.length
            self.send_session_update()
        self._update_status()

    @reaper_access
    def select_take(self, number):
        project = reapy.Project()
        take = Take.objects.get(session=self.session_id, number=number)
        project.time_selection = take.location, take.location + take.length
        self.current_take = number
        project.perform_action(40630)  # go to start of selection
        self._update_status()

    @reaper_access
    def take_seek(self, pos):
        take = Take.objects.filter(session=self.session_id, number=self.current_take).first()
        if take:
            print(take.location + pos)
            reapy.Project().cursor_position = take.location + pos
        self._update_status()

    @reaper_access
    def take_play(self):
        reapy.Project().play()
        self._update_status()


    @reaper_access
    def update_status(self):
        self._update_status()


    def _update_status(self):
        if self.status == DISCONNECTED:
            return

        if not self.session_id:
            self.status = CONNECTED
            return

        project = reapy.Project()
        position = 0
        if project.is_playing or project.is_recording and self.current_take:
            take = Take.objects.filter(session=self.session_id, number=self.current_take).first()
            if take:

                position = project.play_position - take.location

        state = 'ready'
        if project.is_recording:
            state = 'recording'
        elif project.is_playing:
            state = 'playing'

        self.status = {
            'position': position,
            'current_take': self.current_take,
            'state': state
        }
        self.send_recorder_update()


    def send_session_update(self):
        async_to_sync(get_channel_layer().group_send)(
            SESSION_ROOM_NAME,
            {
                'type': 'send_session_update',
                'action': 'UPDATE_FULL_SESSION',
            }
        )

    def send_recorder_update(self):
        async_to_sync(get_channel_layer().group_send)(
            SESSION_ROOM_NAME,
            {
                'type': 'send_recorder_update',
                'action': 'RECORDER_UPDATE',
            }
        )


reaper = ReaperRecorder()
reaper.connect()

class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            SESSION_ROOM_NAME,
            self.channel_name
        )

        self.send_json(mutation('ACTIVE_USER', CURRENT_USER))
        self.send_session_update(None)
        self.send_recorder_update()


    def send_recorder_update(self, *args):
        self.send_json(mutation('RECORDER_UPDATE', reaper.status))

    def send_session_update(self, *args):
        session = Session.objects.filter(pk=reaper.session_id).first()
        if session:
            self.send_json(mutation('UPDATE_FULL_SESSION', session.to_dict()))



    def receive_json(self, content, **kwargs):
        if content['action'] == 'login':
            STATUS['user'] = content['data']
            self.send_json(mutation('ACTIVE_USER', STATUS['user']))

        elif content['action'] == 'session_start':
            reaper.start_session(content['data'])
        elif content['action'] == 'take_play':
            reaper.take_play()

        elif content['action'] == 'take_start':
            reaper.start_take()

        elif content['action'] == 'take_seek':
            reaper.take_seek(content['data'])

        elif content['action'] == 'take_stop':
            reaper.stop_take()

        elif content['action'] == 'next_take_name':
            session = Session.objects.filter(pk=reaper.session_id).first()
            if session:
                session.next_take_name = content['data']
                session.save()
                self.send_session_update(None)

        elif content['action'] == 'take_select':
            reaper.select_take(content['data'])
            # STATUS['session']['recorder']['state'] = 'idle'
            # STATUS['session']['recorder']['current_take'] = content['data']
            # self.send_json(mutation('UPDATE_FULL_SESSION', STATUS['session']))

# login / logout
# session_start / session_close
# take_start / take_stop / take_cancel / take_select / take_play / take_seek
# take_next_name


