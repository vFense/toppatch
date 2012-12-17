from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from db.client import *
from db.update_table import *
from db.query_table import *
from db.client import *
from utils.common import verify_json_is_valid
from csrhandler import CsrHandOff
import logging
import logging.config

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('csrlistener')
ENGINE = init_engine()
c = ENGINE.connect()
try:
    c.execute("SELECT * FROM node_info")
    c.close()
except exc.DBAPIError, e:
    logger.debug(e.message)
    c = e.connect()
    c.execute("SELECT * FROM node_info")

class CsrReceiver(Protocol):
    """
       This class does one thing and one thing only.
       It receives a Certificate Request in a Json Message.
       1st it verifies if the message is in a Valid Json Format.
       2nd, it verifies the Json message contains and operation
       the csr. 3rd, it saves the csr in the filesystem. 4th, 
       it then checks if this csr is already in the database.
       If it is not in the database, it than adds it.
    """
    total_data = ""
    def connectionMade(self):
        self.client_peer = self.transport.getPeer()
        self.client_ip = self.client_peer.host
        logger.info('%s - agent %s connected' %\
                ('system_user', self.client_ip)
                )

    def dataReceived(self, data):
        self.total_data = self.total_data + data

    def connectionLost(self, reason):
        self.transport.loseConnection()
        data = self.total_data
        logger.debug('%s - data received from agent %s\n%s' %\
                ('system_user', self.client_ip, data)
                )
        self.total_data = ""
        CsrHandOff(ENGINE, self.client_ip, data)

if __name__ == '__main__':
    f = Factory()
    f.protocol = CsrReceiver
    reactor.listenTCP(9002, f)
    reactor.run()
