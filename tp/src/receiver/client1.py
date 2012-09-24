import json
from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory, Protocol

class EchoClient(Protocol):
    def connectionMade(self):
        #print "hello, world"
        json_data = '{"operation" : "install","transaction_id" : "12234","updates" : [ "updateID1", "updateID2", "updateID3"]}'
        #self.transport.write("hello, world!")
        print json_data
        self.transport.write(json_data)

    def dataReceived(self, data):
        print "Server said:", data
        self.transport.loseConnection()

class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()

class CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv3_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/client/keys/foo.cert')
        ctx.use_privatekey_file('/opt/TopPatch/var/lib/ssl/client/keys/foo.key')
        return ctx

if __name__ == '__main__':
    factory = EchoClientFactory()
    reactor.connectSSL('localhost', 9000, factory, CtxFactory())
    reactor.run()
