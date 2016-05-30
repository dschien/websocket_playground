import logging

import sys
from autobahn.twisted import WebSocketClientProtocol
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

logger = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class SecureServerClientProtocol(WebSocketClientProtocol):
    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.warn("Binary message received: {0} bytes".format(len(payload)))
        else:
            logger.info("Text message received: {0}".format(payload.decode('utf8')))


#
#
# class Greeter(Protocol):
#     def sendMessage(self, msg):
#         self.transport.write("MESSAGE %s\n" % msg)

def gotProtocol(p):
    p.sendMessage("Hello")
    reactor.callLater(1, p.sendMessage, "This is sent in a second")
    reactor.callLater(2, p.transport.loseConnection)


point = TCP4ClientEndpoint(reactor, "localhost", 5678)
d = connectProtocol(point, SecureServerClientProtocol())
d.addCallback(gotProtocol)
reactor.run()
