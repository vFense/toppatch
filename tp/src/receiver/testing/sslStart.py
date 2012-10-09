from OpenSSL import SSL

from twisted.internet import reactor, ssl, defer
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import SSL4ClientEndpoint


class _AgentSender(Protocol):
    def sendMessage(self, msg):
        self.transport.write(msg)

    def dataReceived(self, data):
        self.data = data
        self.transport.loseConnection()

    def connectionLost(self, reason):
        #print self.data, reason.value
#        reactor.stop()
        return (self.data, reason.value)

class _AgentFactory(Factory):
    def buildProtocol(self, addr):
        return _AgentSender()


class _CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv3_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/server/keys/server.cert')
        ctx.use_privatekey_file('/opt/TopPatch/var/lib/ssl/server/keys/server.key')
        return ctx


class SslConnector():
    results = None
    def __init__(self, node, msg):
        self.node = node
        self.msg = msg
        self.port = 9000
        self.point = SSL4ClientEndpoint(reactor, self.node, self.port, _CtxFactory(), 1)
        self.d = self.point.connect(_AgentFactory())
        self.d.addCallback(self._sendMessage)
        self.d.addErrback(self._returnError)
        self.results = self.d
#        reactor.run()

    def _sendMessage(self, proto):
        proto.sendMessage(self.msg)

    def _returnError(self, failure):
#        reactor.stop()
        return (None, failure.value)

#i = 100
#for i in range(i):
#    a = SslConnector('127.0.0.1', '{"operation_id": "1", "operation": "install", "updates": ["2014", "2012", "2013"]}')
#    print a.results
#reactor.run()
