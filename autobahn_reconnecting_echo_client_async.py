import sys

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


class EchoClientProtocol(WebSocketClientProtocol):
    def sendHello(self):
        self.sendMessage("Hello, world!".encode('utf8'))

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode('utf8')))
        reactor.callLater(1, self.sendHello)


class EchoClientFactory(ReconnectingClientFactory, WebSocketClientFactory):
    protocol = EchoClientProtocol

    # http://twistedmatrix.com/documents/current/api/twisted.internet.protocol.ReconnectingClientFactory.html
    #
    maxDelay = 10
    maxRetries = 5

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == '__main__':

    # if len(sys.argv) < 2:
    #     print("Need the WebSocket server address, i.e. ws://127.0.0.1:9000")
    #     sys.exit(1)

    log.startLogging(sys.stdout)

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = EchoClientFactory('ws://127.0.0.1:5678')

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 5678)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
