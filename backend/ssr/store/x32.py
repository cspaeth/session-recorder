import datetime
import logging
import time
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

        self.last_command = None
        self.cache = {}

        dispatch = dispatcher.Dispatcher()
        dispatch.set_default_handler(self.dispatch_to_room)
        server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 10033), dispatch)
        self.client = X32UdpClient("192.168.178.21", 10023, server)
        self.client.send_message("/xinfo", [])

        Thread(target=self.keep_alive).start()
        Thread(target=server.serve_forever).start()
        self.initial_sync()

    def initial_sync(self):
        properties = []
        for channel in range(1, 32):
            properties.append(f'/ch/{channel:02}/mix/fader')
            properties.append(f'/ch/{channel:02}/mix/on')
            properties.append(f'/ch/{channel:02}/config/name')
            properties.append(f'/ch/{channel:02}/config/color')


            # for bus in range(1, 16):
            #     properties.append(f'/ch/{channel:02}/mix/{bus:02}/level')
            #
            #     properties.append(f'/ch/{channel:02}/mix/{bus:02}/on')


        # print(len(properties))
        start = time.time()
        for prop in properties:
            self.x32_request_value([prop])
        end = time.time()
        print(":::: "  + str(end - start))
        print(end - start)

    def keep_alive(self):
        while True:
            self.client.send_message("/xremote", [])
            # self.client.send_message("/xinfo", [])
            sleep(7)
            # pprint(self.cache)
            # self.update_module_status()

    @action
    def x32_send_value(self, message):
        # print("sending request value to x32 (%s): (%s) " % (message[0], message[1]))
        self.client.send_message(message[0], message[1])
        send_to_group(settings.MIXER_GROUP_NAME, 'osc_input', message)

    @action
    def x32_request_value(self, message):
        # print("sending request value to x32 (%s) " % message[0])
        self.client.send_message(message[0], None)

    def dispatch_to_room(self, *a, **ab):
        self.last_command = datetime.datetime.now()
        self.cache[a[0]] = a[1]
        # print("received from x32: (%s) " % str(a))
        send_to_group(settings.MIXER_GROUP_NAME, 'osc_input', a)

    def get_module_status(self):

        return { 'osc': self.cache}

