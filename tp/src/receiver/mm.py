
import sys
import os
from OpenSSL import SSL, crypto
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.python import log

from tools.ssl import *

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

ALLOWED_CIPHER_LIST = 'TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH'
SERVER_KEY_DIR = '/opt/TopPatch/var/lib/ssl/server/keys/'
CLIENT_KEY_DIR = '/opt/TopPatch/var/lib/ssl/client/keys/'
SERVER_PRIVKEY_NAME  = 'server.key'
SERVER_PUBKEY_NAME   = 'server.cert'
CA_PRIVKEY_NAME  = 'CA.key'
CA_PUBKEY_NAME   = 'CA.cert'
TOPPATCH_CA = ('TopPatch Certficate Authority', 'TopPatch',
        'Remediation Vault', 'US', 'NY', 'NYC')
TOPPATCH_SERVER = ('TopPatch Server', 'TopPatch',
        'Remediation Vault', 'US', 'NY', 'NYC')
EXPIRATION = (0, 60*60*24*365*10)

SERVER_PRIVKEY = SERVER_KEY_DIR + SERVER_PRIVKEY_NAME
SERVER_PUBKEY = SERVER_KEY_DIR + SERVER_PUBKEY_NAME
CA_PRIVKEY = SERVER_KEY_DIR + CA_PRIVKEY_NAME
CA_PUBKEY = SERVER_KEY_DIR + CA_PUBKEY_NAME
class ServerContextFactory:
    
    def _verify(self, connection, x509, errnum, errdepth, ok):
        if ok:
            return True
        else:
            return False

    def getContext(self):
        """Create an SSL context.
        This is a sample implementation that loads a certificate from a file 
        called 'server.pem'."""
        ctx = SSL.Context(SSL.SSLv3_METHOD)
        ctx.set_cipher_list(ALLOWED_CIPHER_LIST)
        ctx.use_certificate_file(SERVER_PUBKEY)
        ctx.use_privatekey_file(SERVER_PRIVKEY)
        ctx.load_verify_locations(CA_PUBKEY)
        ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
                       self._verify)
        ctx.set_verify_depth(10)
        return ctx

#import echoserv
#class Echo(Protocol):
#    def dataReceived(self, data):
#        """As soon as any data is received, write it back."""
#        self.transport.write(data)

class TopPatchMain(Protocol):

    def connectionMade(self):
        print 'connectionMade', self.transport.getPeerCertificate()
        #return Echo.connectionMade(self)

    def dataReceived(self, data):
        print 'dataReceived', self.transport.getPeerCertificate()
        self.transport.write(data)
        #return Echo.dataReceived(self, data)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    try:
        file_exists = os.stat(SERVER_PRIVKEY)
    except OSError as e:
        print 'Creating Certificate Authority and Server Keys'
        ca_pkey = generatePrivateKey(TYPE_RSA, 4098)
        ca_cert = createCertificateAuthority(ca_pkey, 1,
                TOPPATCH_CA, EXPIRATION
                )
        server_pkey = generatePrivateKey(TYPE_RSA, 4098)
        server_csr = createCertRequest(server_pkey, TOPPATCH_SERVER)
        server_cert = createSignedCertificate(server_csr,
                (ca_cert, ca_pkey), 1, EXPIRATION
                )
        saveKey(SERVER_KEY_DIR, ca_pkey, '.key', name='CA')
        saveKey(SERVER_KEY_DIR, ca_cert, '.cert', name='CA')
        saveKey(SERVER_KEY_DIR, server_pkey, '.key', name='server')
        saveKey(SERVER_KEY_DIR, server_csr, '.csr', name='server')
        saveKey(SERVER_KEY_DIR, server_cert, '.cert', name='server')
    factory = Factory()
    factory.protocol = TopPatchMain
    reactor.listenSSL(9000, factory, ServerContextFactory())
    reactor.run()
