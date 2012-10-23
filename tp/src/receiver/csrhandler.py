from json import loads, dumps
from time import sleep
from jsonpickle import encode
from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import verifyJsonIsValid
from utils.ssltools import *
from utils.tcpasync import TcpConnect

class CsrHandOff():
    def __init__(self, ENGINE, ip_address, data):
        self.data = None
        self.csr_path = None
        self.csr_name = None
        self.csr_error =  None
        self.csr_row = None
        self.signed_cert = None
        self.path_to_cert = None
        self.cert_name = None
        self.cert_error = None
        self.error = None
        self.client_ip = ip_address
        self.valid_json, self.json_object = verifyJsonIsValid(data)
        print data
        if self.valid_json:
            self.data = self.json_object
            print self.data
            self.session = createSession(ENGINE)
            if "pem" in self.json_object:
                self.csr_exists, self.csr_oper = csrExists(self.session,
                    self.client_ip)
                if not self.csr_exists:
                    verified, self.error = \
                        verifyValidFormat(self.data['pem'], TYPE_CSR)
                    if verified:
                        self.csr, self.csr_path, self.csr_name, \
                            self.csr_row = storeCsr(self.session, \
                                    self.client_ip, self.data['pem'])
                        self.signed_cert = signCert(self.session, self.csr)
                        self.node, self.cert_path = storeCert(self.session, \
                                self.client_ip, self.signed_cert)
                        self.results = self.sendCert(self.node, \
                            self.signed_cert)
                        print self.results.error, self.results.read_data
                        if self.results.error:
                            self.csr_exists, self.csr_oper = \
                                    csrExists(self.session, self.client_ip)
                            self.cert_exists, self.cert_oper = \
                                    certExists(self.session, self.node.id)
                            csr_file_deleted = os.remove(self.csr_path)
                            cert_file_deleted = os.remove(self.cert_path)
                            print csr_file_deleted
                            print cert_file_deleted
                            self.cert_oper.delete()
                            self.csr_oper.delete()
                            self.node, self.node_exists = \
                                    nodeExists(self.session, node_ip=self.client_ip)
                            if self.node_exists:
                                self.node.delete()
                            self.session.commit()


                else:
                    print 'csr for %s %s' % (self.client_ip, self.error)
            self.session.close()
        else:
            print "JSON NOT VALID"

    def sendCert(self, node, cert):
        sleep(3)
        msg = encode({"node_id" : node.id, "pem" : dumpCert(cert)})
        tcp_results = TcpConnect(self.client_ip, msg, secure=False)
        return tcp_results
