from OpenSSL import SSL, crypto

class ServerContextFactory:
    
    def _verify(self, connection, x509, errnum, errdepth, ok):
        print '_verify (ok=%d):' % ok
        print '  subject:', x509.get_subject()
        print '  issuer:', x509.get_issuer()
        print '  errnum %s, errdepth %d' % (errnum, errdepth)
        return False # ok

    def getContext(self):
        """Create an SSL context.
        
        This is a sample implementation that loads a certificate from a file 
        called 'server.pem'."""
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        print dir(ctx)
        ctx.use_certificate_file('serv.crt')
        ctx.use_privatekey_file('serv.pem')
        print 'Context additions'
        ctx.load_client_ca('client.crt')
        ctx.load_verify_locations('client.crt')
        ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
                       self._verify)
        print 'verify depth:', ctx.get_verify_depth()
        ctx.set_verify_depth(10)
        print 'verify depth:', ctx.get_verify_depth()
        return ctx

import echoserv

class MyProtocol(echoserv.Echo):

    def connectionMade(self):
        print 'connectionMade', self.transport.getPeerCertificate()
        return echoserv.Echo.connectionMade(self)

    def dataReceived(self, data):
        print 'dataReceived', self.transport.getPeerCertificate()
        return echoserv.Echo.dataReceived(self, data)


if __name__ == '__main__':
    import echoserv, sys
    from twisted.internet.protocol import Factory
    from twisted.internet import ssl, reactor
    from twisted.python import log
    log.startLogging(sys.stdout)
    factory = Factory()
    factory.protocol = MyProtocol
    reactor.listenSSL(9000, factory, ServerContextFactory())
    reactor.run()
