from OpenSSL import SSL

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import SSL4ClientEndpoint

class SslConnector():
    def __init__(self, node, msg):
        self.node = node
        self.port = 9000
        self.msg = msg
        point = SSL4ClientEndpoint(reactor, self.node, self.port, SslConnector._CtxFactory())
        d = point.connect(SslConnector._AgentFactory())
        d.addCallback(self._sendMessage)
        reactor.run()

    def _sendMessage(self, proto):
        proto.sendMessage(self.msg)


    class _AgentSender(Protocol):
        def sendMessage(self, msg):
            self.transport.write(msg)

        def dataReceived(self, data):
            self.transport.loseConnection()

        def connectionLost(self, reason):
            reactor.stop()

    class _AgentFactory(Factory):
        def buildProtocol(self, addr):
            return SslConnector._AgentSender()


    class _CtxFactory(ssl.ClientContextFactory):
        def getContext(self):
            self.method = SSL.SSLv3_METHOD
            ctx = ssl.ClientContextFactory.getContext(self)
            ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/server/keys/server.cert')
            ctx.use_privatekey_file('/opt/TopPatch/var/lib/ssl/server/keys/server.key')
            return ctx

