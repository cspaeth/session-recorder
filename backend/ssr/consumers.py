from os import mkdir
from shutil import copy

import reapy
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from reapy import reascript_api

SESSION_ROOM_NAME = 'session'

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
            'state': 'idle',
            'current_take': 1,
            'position': 0
        }
    },
}

RECORDER = {
    'CHANNEL_NAME': None
}

def mutation(name, data):
    return {
        'action': name,
        'data': data
    }

HOST_PATH = "/Users/csp/Projects/session-recorder/var"
BASE_PATH = "/sessions/"
BASE_TEMPLATE = BASE_PATH + "template.RPP"

class ReaperRecorder:
    def __init__(self):
        reapy.connect("192.168.178.32")

        self.current_take = None

    def update_position(self, project):
        STATUS['session']['recorder']['position'] = project.play_position

    def send_update(self):
        async_to_sync(get_channel_layer().group_send)(
            SESSION_ROOM_NAME,
            {
                'type': 'send_session_update'
            }
        )

    def start_session(self, name):
        session_dir = BASE_PATH + name
        session_file =  session_dir + "/Session.RPP"
        mkdir(session_dir)
        copy(BASE_TEMPLATE, session_file)
        reapy.open_project(HOST_PATH + session_file)

        if reapy.Project().path.endswith(name):
            STATUS['session']['recorder']['state'] = 'idle'
            STATUS['session']['name'] = name
            self.send_update()
        # check for open project
        # send status idle

    def start_take(self):
        project = reapy.Project()
        project.perform_action(40043)
        start = project.cursor_position

        reascript_api.CSurf_OnRecord()
        if project.is_recording:
            self.current_take = {
                'number': STATUS['session']['next_take']['number'],
                'name': STATUS['session']['next_take']['name'],
                'start': start
            }

            STATUS['session']['takes'].append(self.current_take)
            STATUS['session']['next_take']['number'] += 1

            STATUS['session']['recorder']['state'] = 'record'
        self.send_update()


    def stop_take(self):
        project = reapy.Project()
        project.stop()

        # if project.is_stopped:
        STATUS['session']['recorder']['state'] = 'idle'

        if 'length' not in self.current_take:
            self.current_take['length'] = project.length - self.current_take['start']
        self.current_take = None

        print("w")
        print(STATUS['session']['takes'])
        self.send_update()

    def select_take(self, number):
        for take in STATUS['session']['takes']:
            if take['number'] == number:
                project = reapy.Project()
                project.time_selection = take['start'], take['start'] + take['length']
                STATUS['session']['recorder']['current_take'] = number
                self.update_position(project)
                self.send_update()

reaper = ReaperRecorder()

class RemoteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            SESSION_ROOM_NAME,
            self.channel_name
        )

        self.send_json(mutation('UPDATE_FULL_SESSION', STATUS['session']))
        self.send_json(mutation('ACTIVE_USER', STATUS['auth']['user']))


    def send_session_update(self, content):
        self.send_json(mutation('UPDATE_FULL_SESSION', STATUS['session']))

    def receive_json(self, content, **kwargs):
        if content['action'] == 'login':
            STATUS['user'] = content['data']
            self.send_json(mutation('ACTIVE_USER', STATUS['user']))

        elif content['action'] == 'session_start':
            reaper.start_session(content['data'])

        elif content['action'] == 'take_start':
            reaper.start_take()

        elif content['action'] == 'take_stop':
            reaper.stop_take()

        elif content['action'] == 'next_take_name':
            STATUS['session']['next_take']['name'] = content['data']
            self.send_json(mutation('UPDATE_FULL_SESSION', STATUS['session']))

        elif content['action'] == 'take_select':
            reaper.select_take(content['data'])
            # STATUS['session']['recorder']['state'] = 'idle'
            # STATUS['session']['recorder']['current_take'] = content['data']
            # self.send_json(mutation('UPDATE_FULL_SESSION', STATUS['session']))

# login / logout
# session_start / session_close
# take_start / take_stop / take_cancel / take_select / take_play / take_seek
# take_next_name


