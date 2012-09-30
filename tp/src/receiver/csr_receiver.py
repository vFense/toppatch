#!/usr/bin/env python

from json import loads, dumps
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from db.client import connect as db_connect
import tools.ssl as ssl_tools
from tools.common import verifyJsonIsValid
from db.query_table import *
from db.update_table import *


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
    def dataReceived(self, data):
        if verifyJsonIsValid(data):
            data = loads(data)
            if data['operation'] == 'send_csr' \
                    and data['csr'] is not None:
                self.session = db_connect()
                self.client_ip = self.transport.getPeer()
                self.csr_exists = csrExists(self.session,
                    self.client_ip.host)
                if not self.csr_exists:
                    addCsr(self.session, self.client_ip.host,
                        ssl_tools.SSL_CLIENT_CSR_DIR )
                    self.csr_exists = csrExists(self.session,
                        self.client_ip.host)
                verified, error = ssl_tools.verifyValidFormat(data['csr'],
                    ssl_tools.TYPE_CSR)
                if verified:
                    self.path_to_csr, self.csr_error = \
                        ssl_tools.saveKey(ssl_tools.CLIENT_CSR_DIR,
                            data['csr'], ssl_tools.TYPE_CSR,
                            name=self.client_ip.host)
                else:
                    print 'csr for %s %s' % (self.client_ip.host, error)

if __name__ == '__main__':
    f = Factory()
    f.protocol = CsrReceiver
    reactor.listenTCP(8000, f)
    reactor.run()
