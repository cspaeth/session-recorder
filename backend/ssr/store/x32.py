import logging
from collections import OrderedDict
from threading import Thread
from time import sleep

from django.conf import settings
from pythonosc import dispatcher, osc_server
from pythonosc import udp_client

from ssr.store.util import StateModule, action
from ssr.utils import send_to_group

log = logging.getLogger(__name__)

DISCONNECTED = {
    'state': "disconnected"
}

CONNECTED = {
    'state': 'connected'
}

MAX_RETRIES = 3000
RETRY_SLEEP_LENGHT = .01


class X32UdpClient(udp_client.SimpleUDPClient):

    def __init__(self, address, port, server, allow_broadcast=False):
        self._sock = server.socket.dup()
        self._sock.setblocking(0)
        if allow_broadcast:
            self._sock.setsockopt(self._sock.SOL_SOCKET, self._sock.SO_BROADCAST, 1)

        self._address = address
        self._port = port


class X32Module(StateModule):

    def __init__(self):
        super().__init__()

        self.cache = {}
        log.info("Starting X32 connection")
        dispatch = dispatcher.Dispatcher()
        dispatch.set_default_handler(self.dispatch_to_room)
        server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 10033), dispatch)
        # self.client = X32UdpClient("192.168.1.164", 10023, server)
        self.client = X32UdpClient("192.168.100.136", 10023, server)


        self.messages = OrderedDict()

        # Master Faders (Main bus, Mono bus)
        self.messages[f'/main/st/mix/fader'] = float
        self.messages[f'/main/st/config/name'] = str
        self.messages[f'/main/st/config/color'] = int
        self.messages[f'/main/m/mix/fader'] = float
        self.messages[f'/main/m/config/name'] = str
        self.messages[f'/main/m/config/color'] = int

        # Regular Channels
        for channel in range(1, 33):
            # Main bus send, mute
            self.messages[f'/ch/{channel:02}/mix/fader'] = float
            self.messages[f'/ch/{channel:02}/mix/on'] = int
            # Mono bus send, mute
            self.messages[f'/ch/{channel:02}/mix/mlevel'] = float
            self.messages[f'/ch/{channel:02}/mix/mono'] = int
            # Name and Color
            self.messages[f'/ch/{channel:02}/config/name'] = str
            self.messages[f'/ch/{channel:02}/config/color'] = int

        # Aux Channels
        for aux in range(1, 9):
            # Main bus send, mute
            self.messages[f'/auxin/{aux:02}/mix/fader'] = float
            self.messages[f'/auxin/{aux:02}/mix/on'] = float

            self.messages[f'/auxin/{aux:02}/mix/mlevel'] = float
            self.messages[f'/auxin/{aux:02}/mix/mono'] = float
            # Name and Color
            self.messages[f'/auxin/{aux:02}/config/name'] = str
            self.messages[f'/auxin/{aux:02}/config/color'] = int

        # FX Return Channels
        for fxrtn in range(1, 9):
            # Main bus send, mute
            self.messages[f'/fxrtn/{fxrtn:02}/mix/fader'] = float
            self.messages[f'/fxrtn/{fxrtn:02}/mix/on'] = float
            # Mono bus send, mute
            self.messages[f'/fxrtn/{fxrtn:02}/mix/mlevel'] = float
            self.messages[f'/fxrtn/{fxrtn:02}/mix/mono'] = float
            # Name and Color
            self.messages[f'/fxrtn/{fxrtn:02}/config/name'] = str
            self.messages[f'/fxrtn/{fxrtn:02}/config/color'] = int

        # Buses
        for bus in range(1, 17):
            # Bus main level, mute
            self.messages[f'/bus/{bus:02}/mix/fader'] = float
            self.messages[f'/bus/{bus:02}/mix/on'] = float
            # Name and Color
            self.messages[f'/bus/{bus:02}/config/name'] = str
            self.messages[f'/bus/{bus:02}/config/color'] = int

            # Stereo link (every other channel)
            if bus % 2 == 1:
                self.messages[f'/config/buslink/{bus}-{bus+1}'] = int

            # Regular channels (level, mute)
            for channel in range(1, 33):
                self.messages[f'/ch/{channel:02}/mix/{bus:02}/level'] = float
                self.messages[f'/ch/{channel:02}/mix/{bus:02}/on'] = int

            # Aux channels (level, mute)
            for aux in range(1, 9):
                self.messages[f'/auxin/{aux:02}/mix/{bus:02}/level'] = float
                self.messages[f'/auxin/{aux:02}/mix/{bus:02}/on'] = int

            # Fx return channels (level, mute)
            for fxrtn in range(1, 9):
                self.messages[f'/fxrtn/{fxrtn:02}/mix/{bus:02}/level'] = float
                self.messages[f'/fxrtn/{fxrtn:02}/mix/{bus:02}/on'] = int


        log.info("Starting keep_alive thread")
        Thread(target=self.keep_alive).start()

        log.info("Starting osc event handler thread")
        Thread(target=server.serve_forever).start()

        log.debug("Requesting %i properties" % len(self.messages))
        Thread(target=self.full_sync).start()

    def full_sync(self):
        log.info(f'Full Sync, clearing cache ({len(self.messages)} Props)')
        self.cache = {}

        for prop in self.messages.keys():
            self.x32_request_value([prop])
            retry_count = 0
            while prop not in self.cache:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    log.warning(f'No value received for {prop}')
                    break
                sleep(RETRY_SLEEP_LENGHT)
        log.info("... Sync completed")
        self.update_module_status()

    def keep_alive(self):
        while True:
            log.debug("Sending keep alive (/xremote)")
            self.client.send_message("/xremote", [])
            sleep(7)


    @action
    def x32_send_value(self, message):
        path, value = message
        log.debug("Sending value to x32 and group (%s): (%s) " % (path, value))

        if path in self.messages:
            value = self.messages[path](value)

        self.client.send_message(path, value)
        send_to_group(settings.MIXER_GROUP_NAME, 'osc_input', message)

    @action
    def x32_request_value(self, message):
        log.debug("Sending value request to x32 (%s) " % message[0])
        self.client.send_message(message[0], None)

    def dispatch_to_room(self, *a, **ab):
        path, value = a

        if path in self.messages:
            log.debug(f"Received from x32, send to group: ({path}={value})")
            self.cache[path] = value
            send_to_group(settings.MIXER_GROUP_NAME, 'osc_input', a)
        else:
            log.info(f'Unhandled OSC command from x32: {path}={value}')

    def get_module_status(self):
        return {'osc': self.cache}

