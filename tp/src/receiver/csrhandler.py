from json import loads, dumps

from utils.db.client import *
import utils.ssl as ssl_tools
from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import verifyJsonIsValid

class CsrHandoff():
    def __init__(self, ENGINE, ip_address, data):
        if verifyJsonIsValid(data):
            data = loads(data)
            if pem in data:
                self.session = createSession(ENGINE)
                self.client_ip = ip_address
                self.csr_exists = csrExists(self.session,
                    self.client_ip)
                if not self.csr_exists:
                    verified, error = ssl_tools.verifyValidFormat(data['csr'],
                        ssl_tools.TYPE_CSR)
                    if verified:
                        self.path_to_csr, self.csr_error = \
                            ssl_tools.saveKey(ssl_tools.CLIENT_CSR_DIR,
                                data['csr'], ssl_tools.TYPE_CSR,
                                name=self.client_ip.host)
                        csr_row = addCsr(self.session, self.client_ip.host,
                            ssl_tools.SSL_CLIENT_CSR_DIR )
                else:
                    print 'csr for %s %s' % (self.client_ip.host, error)
                self.session.close()


