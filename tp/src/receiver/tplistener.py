from json import loads, dumps
from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from addupdates import *
from dbquery import *


ALLOWED_CIPHER_LIST = 'TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH'
OPERATION = 'operation'
OPERATION_ID = 'operation_id'
INSTALL = 'install'
SYSTEM_INFO = 'system_info'


class GetJson(Protocol):
    def connectionMade(self):
        self.db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
        Session = sessionmaker(bind=self.db)
        self.session = Session()
        self.client_ip = self.transport.getPeer()
        self.node_exists = nodeExists(self.session,
            self.client_ip.host)
        if not self.node_exists:
            addNode(self.session, self.client_ip.host)
            self.node_exists = nodeExists(self.session,
                self.client_ip.host)
    def dataReceived(self, data):
        try:
            json_data = loads(data)
        except ValueError as e:
            print e 
        print json_data
        if json_data[OPERATION] == SYSTEM_INFO:
            addSystemInfo(self.session, json_data,
                self.node_exists)
        self.transport.write(dumps(json_data))

def verifyCallback(connection, x509, errnum, errdepth, ok):
    if not ok:
        print 'invalid cert from subject:', x509.get_subject()
        return False
    else:
        print "Certs are fine"
    return True

if __name__ == '__main__':
    factory = Factory()
    factory.protocol = GetJson

    myContextFactory = ssl.DefaultOpenSSLContextFactory(
        '/opt/TopPatch/var/lib/ssl/server/keys/server.key', '/opt/TopPatch/var/lib/ssl/server/keys/server.cert'
        )

    ctx = myContextFactory.getContext()
    ctx.set_cipher_list(ALLOWED_CIPHER_LIST)
    ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/server.cert")
    ctx.set_verify(
        SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
        verifyCallback
        )

    # Since we have self-signed certs we have to explicitly
    # tell the server to trust them.

    reactor.listenSSL(9000, factory, myContextFactory)
    reactor.run()
