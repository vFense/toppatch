from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol

class Echo(Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

def verifyCallback(connection, x509, errnum, errdepth, ok):
    if not ok:
        print 'invalid cert from subject:', x509.get_subject()
        return False
    else:
        print "Certs are fine"
    return True

if __name__ == '__main__':
    factory = Factory()
    factory.protocol = Echo

    myContextFactory = ssl.DefaultOpenSSLContextFactory(
        '/opt/TopPatch/var/lib/ssl/server/keys/server.key','/opt/TopPatch/var/lib/ssl/server/keys/server.cert', SSL.SSLv3_METHOD
        )

    ctx = myContextFactory.getContext()
    #ctx = SSL.Context(SSL.SSLv3_METHOD)
    ctx.set_cipher_list('TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH')

    ctx.set_verify(
        SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
        verifyCallback
        )

    # Since we have self-signed certs we have to explicitly
    # tell the server to trust them.
    ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/CA.cert")

    reactor.listenSSL(9000, factory, myContextFactory)
    reactor.run()
