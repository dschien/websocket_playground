import logging
import sys

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS

import secure_auth

logger = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class AliveLoggingReceivingCallbackWebsocketClientProtocol(WebSocketClientProtocol):
    """
    Receive only websocket client that logs an alive message when connected.
    """
    alive = False
    callback = None

    def onMessage(self, payload, isBinary):
        if not isBinary:
            self.callback(payload)
            # print("Text message received: {}".format(payload.decode('utf8')))

    def log_alive(self):
        """
        Log alive flag every interval
        :return:
        """
        if self.alive:
            logger.info('Alive')
        reactor.callLater(2, self.log_alive)

    def connectionMade(self):
        """
        Start logging when connected
        :return:
        """
        self.alive = True
        reactor.callLater(2, self.log_alive)
        super().connectionMade()


class CallbackProtocolFactory(ReconnectingClientFactory, WebSocketClientFactory):
    protocol = AliveLoggingReceivingCallbackWebsocketClientProtocol

    maxDelay = 10
    maxRetries = 10

    def __init__(self, *args, callback=None, **kwargs):
        self.callback = callback
        super().__init__(*args, **kwargs)

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        self._p.alive = False

        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def buildProtocol(self, addr):
        self._p = WebSocketClientFactory.buildProtocol(self, addr)
        self._p.callback = self.callback
        return self._p


def run(url, callback):
    factory = CallbackProtocolFactory(ws_url, callback=callback)
    factory.callBack = callback
    connectWS(factory)

    reactor.run()


def callback(payload):
    print("Text message received: {}".format(payload.decode('utf8')))


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    ak, ak_id = secure_auth.get_auth_tokens()
    ws_url = secure_auth.get_websocket_url(ak, ak_id)
    run(ws_url, callback)
