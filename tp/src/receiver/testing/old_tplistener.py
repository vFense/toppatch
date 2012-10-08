from json import loads, dumps
from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol

from jsonpickle import encode, decode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.update_table import *
from db.query_table import *
from db.client import connect as db_connect
from tools.common import verifyJsonIsValid


ALLOWED_CIPHER_LIST = 'TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH'
OPERATION = 'operation'
OPERATION_ID = 'operation_id'
INSTALL = 'install'
SYSTEM_INFO = 'system_info'


class GetJson(Protocol):
    def connectionMade(self):
        print self.transport.getPeer()
    def dataReceived(self, data):
#        foo = encode(data)
        #bar = decode(data)
#        loads(foo)
#        loads(data)
        print data
        valid_json = verifyJsonIsValid(data)
        print valid_json
        if valid_json[0]:
            json_data = valid_json[1]
            self.session = db_connect()
            self.client_ip = self.transport.getPeer()
            self.node_exists = nodeExists(self.session,
                self.client_ip.host)
            if not self.node_exists:
                addNode(self.session, self.client_ip.host)
                self.node_exists = nodeExists(self.session,
                    self.client_ip.host)
            if json_data[OPERATION] == SYSTEM_INFO:
                addSystemInfo(self.session, json_data,
                    self.node_exists)
            self.session.commit()
            print "session committed"
            self.session.close()
            print "session closed"
            self.transport.write(dumps(json_data))

    def connectionLost(self, reason):
         #print reason.printDetailedTraceback
         print reason.value

    def connectionDone(self, reason):
         #print dir(reason)
         print reason.printDetailedTraceback

    def connectionAborted(self, reason):
         print reason.printDetailedTraceback

    def SSLrror(self, reason):
         print reason.printDetailedTraceback

    def PeerVerifyError(self, reason):
         print reason.printDetailedTraceback

    def CertificateError(self, reason):
         print reason.printDetailedTraceback





def verifyCallback(connection, x509, errnum, errdepth, ok):
    if not ok:
        print 'invalid cert from subject:', x509.get_subject()
        return False
    else:
        print "Certs are fine", x509.get_subject(), x509.get_issuer()
        return True

if __name__ == '__main__':
    factory = Factory()
    factory.protocol = GetJson

    myContextFactory = ssl.DefaultOpenSSLContextFactory(
        '/opt/TopPatch/var/lib/ssl/server/keys/server.key',
        '/opt/TopPatch/var/lib/ssl/server/keys/server.cert',
        #SSL.TLSv1_METHOD
        #SSL.SSLv23_METHOD
        )

    ctx = myContextFactory.getContext()
    ctx.set_cipher_list(ALLOWED_CIPHER_LIST)
    ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/server.cert")
    print "Im goint to verify you in the mouth"
    #ctx.set_verify(
    #    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT | SSL.VERIFY_CLIENT_ONCE,
    #    verifyCallback
    #    )
    print "YOU HAVE BEEN VERIFIED"

    reactor.listenSSL(9000, factory, myContextFactory)
    reactor.run()
