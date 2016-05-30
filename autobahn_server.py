#!/usr/bin/env python

import simplejson as json
from twisted.internet import task
from twisted.internet import reactor

ws_push_data = {"DataType": 0, "Data": {
    "GDDO": {"GMACID": 46477239136514, "GCS": "1", "GN": "UOB00012", "LUT": "2016-05-27T13:43:42.686", "ZNDS": [
        {"ZID": 1, "DDDO": [{"DRefID": 262912, "DPID": 64,
                             "DPDO": [{"DPRefID": 309, "CV": "900", "LUT": "2016-04-20T08:22:08"},
                                      {"DPRefID": 306, "CV": "10", "LUT": "2016-04-20T08:22:07"},
                                      {"DPRefID": 305, "CV": "1", "LUT": "2016-05-27T10:58:48"},
                                      {"DPRefID": 301, "CV": "255", "LUT": "2016-05-27T13:43:44"},
                                      {"DPRefID": 308, "CV": "300", "LUT": "2016-04-20T08:22:07"},
                                      {"DPRefID": 304, "CV": "0.16", "LUT": "2016-05-26T11:58:52"},
                                      {"DPRefID": 307, "CV": "1.0", "LUT": "2016-04-20T08:22:07"}]},
                            {"DRefID": 263168, "DPID": 64,
                             "DPDO": [{"DPRefID": 309, "CV": "900", "LUT": "2016-04-20T08:22:38"},
                                      {"DPRefID": 306, "CV": "10", "LUT": "2016-04-20T08:22:37"},
                                      {"DPRefID": 301, "CV": "255", "LUT": "2016-05-27T10:55:45"},
                                      {"DPRefID": 304, "CV": "0.02", "LUT": "2016-04-27T19:25:37"},
                                      {"DPRefID": 305, "CV": "0", "LUT": "2016-05-27T12:48:46"},
                                      {"DPRefID": 307, "CV": "1.0", "LUT": "2016-04-20T08:22:37"},
                                      {"DPRefID": 308, "CV": "300", "LUT": "2016-04-20T08:22:38"}]},
                            {"DRefID": 131328, "DPID": 64,
                             "DPDO": [{"DPRefID": 113, "CV": "1", "LUT": "2016-04-20T08:19:07"},
                                      {"DPRefID": 211, "CV": "21", "LUT": "2016-04-20T08:19:12.010752"},
                                      {"DPRefID": 202, "CV": "24.8", "LUT": "2016-05-27T12:39:55"},
                                      {"DPRefID": 212, "CV": "16", "LUT": "2016-04-20T08:19:12.010752"},
                                      {"DPRefID": 101, "CV": "35", "LUT": "2016-05-27T10:39:55"},
                                      {"DPRefID": 201, "CV": "23.0", "LUT": "2016-05-27T11:24:55"},
                                      {"DPRefID": 112, "CV": "900", "LUT": "2016-04-20T08:19:07"},
                                      {"DPRefID": 111, "CV": "Thermostat", "LUT": "2016-04-20T08:19:12.010752"}]},
                            {"DRefID": 263424, "DPID": 64,
                             "DPDO": [{"DPRefID": 301, "CV": "0", "LUT": "2016-04-21T14:47:27"},
                                      {"DPRefID": 107, "CV": "0", "LUT": "2016-04-20T08:24:24"},
                                      {"DPRefID": 102, "CV": "0", "LUT": "2016-04-20T08:24:23"}]}]}]}, "ALMS": []}}

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.echo = task.LoopingCall(self.echo_print)
        self.echo.start(1)

    def echo_print(self):
        self.factory.broadcast(json.dumps(ws_push_data).encode("utf-8"))
        # self.sendMessage(json.dumps(ws_push_data).encode("utf-8"), True)

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast("tick %d from server" % self.tickcount)
        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = BroadcastServerFactory
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 5678)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()