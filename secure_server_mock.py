#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
from twisted.internet import task

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


import simplejson as json

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.callback = PeriodicCallback(self.send_hello, 2000)
        self.callback.start()

    def send_hello(self):
        self.write_message(json.dumps(ws_push_data))

    def on_message(self, message):
        pass

    def on_close(self):
        self.callback.stop()


application = tornado.web.Application([
    (r'/.*', WSHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(5678)
    tornado.ioloop.IOLoop.instance().start()
