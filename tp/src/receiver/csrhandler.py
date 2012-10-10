from json import loads, dumps

from utils.db.client import *

from utils.ssltools import *
from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import verifyJsonIsValid
from utils.tcpasync import TcpConnect

class CsrHandoff():
    def __init__(self, ENGINE, ip_address, data):
        self.data = None
        self.path_to_csr = None
        self.csr_name = None
        self.csr_error =  None
        self.csr_row = None
        self.valid_json, self.json_object = verifyJsonIsValid(data)
        if self.valid_json:
            self.data = loads(self.json_object)
            if pem in self.json_object:
                self.session = createSession(ENGINE)
                self.client_ip = ip_address
                self.csr_exists = csrExists(self.session,
                    self.client_ip)
                if not self.csr_exists:
                    verified, error = \
                        verifyValidFormat(self.data['csr'],
                            ssl_tools.TYPE_CSR)
                    if verified:
                        is_csr_stored = self.storeCsr()
                        if is_csr_stored:
                            self.storeCert()

                else:
                    print 'csr for %s %s' % (self.client_ip.host, error)
                self.session.close()
    def storeCsr():
        self.path_to_csr, self.csr_name, self.csr_error = \
                saveKey(CLIENT_CSR_DIR, self.data['csr'], TYPE_CSR, 
                    name=self.client_ip)
        if not self.csr_error:
            self.csr_row = addCsr(self.session, self.client_ip,
                self.path_to_csr, self.csr_name)
            return True
        else
            return False

    def signCert()
        server_cert = loadCert()
        server_pkey = loadPrivateKey()
        self.client_cert = createSignedCertificate(self.path_to_csr,
            (server_cert, server_pkey), 1, EXPIRATION)
        return self.storeCert()

    def storeCert()
        self.path_to_cert, self.cert_name, self.cert_error = \
                saveKey(CLIENT_KEY_DIR, self.client_cert TYPE_CERT, 
                    name=self.client_ip)
        self.node = addNode(self.session, self.client_ip)
        self.cert_row = addCert(self.session, self.node.id, self.csr_row.id,
                                self.path_to_cert, self.cert_name)
        self.csr_row.update({"is_csr_signed" : True, 
                             "csr_signed_date" : datetime.now()})
        tcp_results = TcpConnect(self.client_ip, self.json)
        


