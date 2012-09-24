import json
from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory, Protocol

class EchoClient(Protocol):
    def connectionMade(self):
        #print "hello, world"
        #op_install = '{"operation" : "install","transaction_id" : "12234","updates" : [ "updateID1", "updateID2", "updateID3"]}'
        op_system_info = '{"operation" : "system_info", "operation_id" : 1, "os_code" : "windows", "os_string" : "Windows 7", "os_version_major" : "", "os_version_minor" : "", "os_version_build" : "", "os_meta" : ""}'
        #self.transport.write("hello, world!")
        print op_system_info
        self.transport.write(op_system_info)

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
        ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/client/keys/client.cert')
        ctx.use_privatekey_file('/opt/TopPatch/var/lib/ssl/client/keys/client.key')
        return ctx

if __name__ == '__main__':
    factory = EchoClientFactory()
    reactor.connectSSL('localhost', 9000, factory, CtxFactory())
    reactor.run()
