from json import loads, dumps
from time import sleep
import logging
import logging.config
from jsonpickle import encode
from db.update_table import *
from db.query_table import *
from db.client import *
from utils.common import verify_json_is_valid
from utils.ssltools import *
from networking.tcpasync import TcpConnect

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('csrlistener')


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
        self.valid_json, self.json_object = verify_json_is_valid(data)
        if self.valid_json:
            self.data = self.json_object
            self.session = create_session(ENGINE)
            self.session = validate_session(self.session)
            if "pem" in self.json_object:
                self.csr_exists = csr_exists(self.session,
                    self.client_ip)
                if not self.csr_exists:
                    verified, self.error = \
                        verify_valid_format(self.data['pem'], TYPE_CSR)
                    if verified:
                        self.csr, self.csr_path, self.csr_name, \
                            self.csr_row = store_csr(self.session, \
                                    self.client_ip, self.data['pem'])
                        self.signed_cert = sign_cert(self.session, self.csr)
                        self.node, self.cert_path = store_cert(self.session, \
                                self.client_ip, self.signed_cert)
                        self.results = self.send_cert(self.node, \
                            self.signed_cert)
                        logger.debug('ERROR: %s\tDATA: %s' % \
                                (self.results.error, self.results.read_data)
                                )
                        if self.results.error:
                            logger.error(self.results.error)
                            logger.error('Deleteing CSR and CERT for %s' %\
                                    (self.results.err)
                                    )
                            self.csr_exists = \
                                    csr_exists(self.session, self.client_ip)
                            self.cert_exists = \
                                    cert_exists(self.session, self.node.id)
                            csr_file_deleted = os.remove(self.csr_path)
                            cert_file_deleted = os.remove(self.cert_path)
                            self.session.delete(self.cert_exists)
                            self.session.delete(self.csr_exists)
                            logger.error('CSR and CERT for %s were deleleted' %\
                                    (self.node.ip_address)
                                    )
                            self.node = \
                                    node_exists(self.session, node_ip=self.client_ip)
                            if self.node:
                                self.session.delete(self.node)
                                logger.error('Deleteing Node %s' %\
                                        (self.node.ip_address)
                                        )
                            self.session.commit()


                else:
                    print 'csr for %s %s' % (self.client_ip, self.error)
            self.session.close()
        else:
            logger.debug('JSON NOT VALID from node %s, msg=%s' % \
                        (ipaddress, data)
                        )


    def send_cert(self, node, cert):
        msg = encode({"node_id" : node.id, "pem" : dump_cert(cert)})
        msg = msg + '<EOF>'
        tcp_results = TcpConnect(self.client_ip, msg, secure=False, timeout=3600)
        return tcp_results


