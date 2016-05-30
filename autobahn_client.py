import sys
from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.asyncio.websocket import WebSocketClientFactory
import logging
from twisted.internet.protocol import ReconnectingClientFactory

logger = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

is_alive = True


class SecureServerClientProtocol(WebSocketClientProtocol):
    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.warn("Binary message received: {0} bytes".format(len(payload)))
        else:
            logger.info("Text message received: {0}".format(payload.decode('utf8')))


class EchoClientFactory(ReconnectingClientFactory, WebSocketClientFactory):
    protocol = SecureServerClientProtocol

    # http://twistedmatrix.com/documents/current/api/twisted.internet.protocol.ReconnectingClientFactory.html
    #
    maxDelay = 10
    maxRetries = 5
    # retries = 50
    #
    # def buildProtocol(self, addr):
    #     logger.debug('Connected.')
    #     logger.debug('Resetting reconnection delay')
    #     self.resetDelay()
    #     return SecureServerClientProtocol()

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


async def alive():
    while is_alive:
        print('alive')
        await asyncio.sleep(2)


if __name__ == '__main__':
    import asyncio

    factory = EchoClientFactory(u"ws://127.0.0.1:5678")
    factory.protocol = SecureServerClientProtocol

    loop = asyncio.get_event_loop()

    # coro = loop.create_connection(factory, 'ws_server', 5678)
    coro = loop.create_connection(factory, '127.0.0.1', 5678)

    loop.run_until_complete(asyncio.wait([
        alive(), coro
    ]))
    loop.run_forever()
    loop.close()
