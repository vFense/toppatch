from OpenSSL import SSL
import sys

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import ssl, reactor

import inspect


class ClientContextFactory(ssl.ClientContextFactory):

    def _verify(self, connection, x509, errnum, errdepth, ok):
        if ok:
            print "yay", x509.get_subject()
            #print "yay", x509.get_issuer()
            return True
        else:
            print "BOOH"
            return False

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/client/keys/client.cert')
        ctx.load_verify_locations('/opt/TopPatch/var/lib/ssl/server/keys/CA.cert')
        ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
                       self._verify)

        return ctx

class EchoClient(LineReceiver):
    end="Bye-bye!"

    def connectionMade(self):
        print "Im here"
        self.sendLine("Hello, world!")
        self.sendLine("What a fine day it is.")
        self.sendLine(self.end)

    def connectionLost(self, reason):
        print 'connection lost (protocol)'

    def lineReceived(self, line):
        x509 = self.transport.getPeerCertificate()
        methods = [x for x in dir(x509)
                   if callable(getattr(x509,x)) and
                   not (x.startswith('set_') or
                        x.startswith('add_') or
                        x.startswith('gmtime_') or
                        x in ('sign','digest'))]
        print "receive:", line
        if line==self.end:
            self.transport.loseConnection()

class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'

    factory = EchoClientFactory()
    reactor.connectSSL(host, 9000, factory, ClientContextFactory())
    reactor.run()

if __name__ == '__main__':
    main()

