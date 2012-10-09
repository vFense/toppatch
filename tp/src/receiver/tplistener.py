from json import loads, dumps
from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol

from jsonpickle import encode, decode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import verifyJsonIsValid
from utils.agentoperation import AgentOperation


ALLOWED_CIPHER_LIST = 'TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH'
OPERATION = 'operation'
OPERATION_ID = 'operation_id'
INSTALL = 'install'
UPDATES_PENDING = 'updates_pending'
UPDATES_INSTALLED = 'updates_installed'
SOFTWARE_INSTALLED = 'system_applications'
SYSTEM_INFO = 'system_info'
STATUS_UPDATE = 'status'
ENGINE = initEngine()


class GetJson(Protocol):
    total_data = ""
    def connectionMade(self):
        print self.transport.getPeer()

    def dataReceived(self, data):
        self.total_data = self.total_data + data

    def connectionLost(self, reason):
        self.transport.loseConnection()
        data = self.total_data
        self.total_data = ""
        valid_json = verifyJsonIsValid(data)
        if valid_json[0]:
            json_data = valid_json[1]
            self.session = createSession(ENGINE)
            self.client_ip = self.transport.getPeer()
            exists, self.node = nodeExists(self.session,
                self.client_ip.host)
            if not self.node:
                addNode(self.session, self.client_ip.host)
                exists, self.node = nodeExists(self.session,
                    self.client_ip.host)
                AgentOperation(self.session, ['{"node_id" : "1", "operation" : "updates_pending"}'])
                AgentOperation(self.session, ['{"node_id" : "1", "operation" : "system_info"}'])
                AgentOperation(self.session, ['{"node_id" : "1", "operation" : "system_applications"}'])
                AgentOperation(self.session, ['{"node_id" : "1", "operation" : "updates_installed"}'])
            if json_data[OPERATION] == SYSTEM_INFO:
                print "system_info", json_data
                addSystemInfo(self.session, json_data,
                    self.node)
            if json_data[OPERATION] == UPDATES_PENDING:
                print "updates_pending", json_data
                addWindowsUpdate(self.session, json_data)
                addWindowsUpdatePerNode(self.session, json_data)
            if json_data[OPERATION] == UPDATES_INSTALLED:
                print "updates_installed", json_data
                addWindowsUpdate(self.session, json_data)
                addWindowsUpdatePerNode(self.session, json_data)
            if json_data[OPERATION] == SOFTWARE_INSTALLED:
                print "software_installed", json_data
                addSoftwareAvailable(self.session, json_data)
                addSoftwareInstalled(self.session, json_data)
            if json_data[OPERATION] == STATUS_UPDATE:
                print "status_update", json_data
                updateNode(self.session, json_data['node_id'])
            if json_data[OPERATION] == INSTALL:
                print "INSTALLED RESULTS", json_data
                addResults(self.session, json_data)
            else:
                pass
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
        '/opt/TopPatch/var/lib/ssl/server/keys/server.key',
        '/opt/TopPatch/var/lib/ssl/server/keys/server.cert',
        #SSL.TLSv1_METHOD
        #SSL.TLSv1_METHOD
        #SSL.SSLv23_METHOD
        )

    ctx = myContextFactory.getContext()
    ctx.set_cipher_list(ALLOWED_CIPHER_LIST)
    ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/server.cert")
    #print "Im goint to verify you in the mouth"
    #ctx.set_verify(
    #    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT | SSL.VERIFY_CLIENT_ONCE,
    #    verifyCallback
    #    )
    #print "YOU HAVE BEEN VERIFIED"

    reactor.listenSSL(9001, factory, myContextFactory)
    reactor.run()
