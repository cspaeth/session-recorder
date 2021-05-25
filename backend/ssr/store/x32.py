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
        self.client = X32UdpClient("192.168.100.136", 10023, server)

        log.info("Starting keep_alive thread")
        Thread(target=self.keep_alive).start()
        log.info("Starting osc event handler thread")
        Thread(target=server.serve_forever).start()

        self.messages = OrderedDict()
        for channel in range(1, 33):
            self.messages[f'/ch/{channel:02}/mix/fader'] = float
            self.messages[f'/ch/{channel:02}/mix/on'] = int
            self.messages[f'/ch/{channel:02}/config/name'] = str

        for aux in range(1, 9):
            self.messages[f'/auxin/{aux:02}/config/name'] = str
            self.messages[f'/auxin/{aux:02}/mix/fader'] = float

        for fxrtn in range(1, 9):
            self.messages[f'/fxrtn/{fxrtn:02}/config/name'] = str
            self.messages[f'/fxrtn/{fxrtn:02}/mix/fader'] = float

        for bus in range(1, 17):
            self.messages[f'/bus/{bus:02}/config/name'] = str
            self.messages[f'/bus/{bus:02}/mix/fader'] = float

            for channel in range(1, 33):
                self.messages[f'/ch/{channel:02}/mix/{bus:02}/level'] = float
                self.messages[f'/ch/{channel:02}/mix/{bus:02}/on'] = int

            for aux in range(1, 9):
                self.messages[f'/auxin/{aux:02}/mix/{bus:02}/level'] = float
                self.messages[f'/auxin/{aux:02}/mix/{bus:02}/on'] = int


            for fxrtn in range(1, 9):
                self.messages[f'/fxrtn/{fxrtn:02}/mix/{bus:02}/level'] = float
                self.messages[f'/fxrtn/{fxrtn:02}/mix/{bus:02}/on'] = int
        # [01..08]/config/name string [12]
            # self.messages[f'/ch/{channel:02}/config/color'] = str
            # self.messages[f'/-ha/{channel-1:02}/index'] = int


        # for headamp in range(127):
        #     self.messages[f'/headamp/{headamp:03}/gain'] = float
        #     self.messages[f'/headamp/{headamp:03}/phantom'] = int

        log.debug("Requesting %i properties" % len(self.messages))

        Thread(target=self.full_sync).start()

    def full_sync(self):
        log.info("Requesting full sync")

        for prop in self.messages.keys():
            self.x32_request_value([prop])
            i = 0
            while not prop in self.cache:
                # log.info("waiting %s" % prop)
                i += 1
                if i > 3000:
                    log.warning("Sync canceled")
                    return
                sleep(.001)
        log.info("... properties requested")

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
        log.debug("Received from x32, send to group: (%s) " % str(a))
        self.cache[a[0]] = a[1]
        send_to_group(settings.MIXER_GROUP_NAME, 'osc_input', a)

    def get_module_status(self):
        return {'osc': self.cache}

