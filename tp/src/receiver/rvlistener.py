from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.client import *
from receiver.rvhandler import HandOff
from scheduler.status_checker import *
from gevent import monkey, thread
#monkey.patch_thread()

ALLOWED_CIPHER_LIST = 'TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH'
ENGINE = init_engine()

class GetJson(Protocol):
    total_data = ""
    def connectionMade(self):
        self.client_peer = self.transport.getPeer()
        self.client_ip = self.client_peer.host
        print self.client_peer

    def dataReceived(self, data):
        self.total_data = self.total_data + data

    def connectionLost(self, reason):
        self.transport.loseConnection()
        data = self.total_data
        print data
        self.total_data = ""
        is_enabled = None
        self.session = create_session(ENGINE)
        node = self.session.query(NodeInfo).\
                filter(NodeInfo.ip_address == self.client_ip).first()
        if node:
            is_enabled = self.session.query(SslInfo).\
                    filter(SslInfo.enabled == True).\
                    filter(SslInfo.node_id == node.id).first()
        if is_enabled:
            handoff = HandOff(ENGINE)
            thread.start_new_thread(handoff.run,
                    args=(data, self.client_ip)).start()

        self.session.close()

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
        '/opt/TopPatch/var/lib/ssl/server/keys/CA.key',
        '/opt/TopPatch/var/lib/ssl/server/keys/CA.cert',
        #SSL.TLSv1_METHOD
        #SSL.TLSv1_METHOD
        #SSL.SSLv23_METHOD
        )

    ctx = myContextFactory.getContext()
    ctx.set_cipher_list(ALLOWED_CIPHER_LIST)
    ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/CA.cert")
    #print "Im goint to verify you in the mouth"
    #ctx.set_verify(
    #    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT | SSL.VERIFY_CLIENT_ONCE,
    #    verifyCallback
    #    )
    #print "YOU HAVE BEEN VERIFIED"

    reactor.listenSSL(9001, factory, myContextFactory)
    reactor.run()
