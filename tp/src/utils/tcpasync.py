import re
import sys
import gevent
from gevent import ssl, socket

class TcpConnect():
    """
    Connect to the remote agent, using the openssl
    library backed by Gevent.
    """
    def __init__(self, host, msg, secure=True):
        slef.secure = secure
        self.host = host
        self.msg = msg
        self.port = 9003
        self.connection_count = 0
        self.write_count = 0
        self.retry = 1
        self.timeout = 30
        self.error = None
        self.read_data = None
        self.tcp, self.tcp_socket = self.socket_init()
        self._connect()

    def socket_init(self):
        new_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if secure:
            new_wrapper = ssl.SSLSocket(new_tcp_socket,
                    keyfile=self.key, certfile=self.cert, ca_certs=self.ca,
                    cert_reqs=ssl.CERT_REQUIRED)
            new_wrapper.timeout = self.timeout
            return new_wrapper
        else:
            new_socket.timeout = self.timeout
            return new_socket

    def _connect(self):
        connected = None
        try:
            self.tcp_socket.connect((self.host, self.port))
            connected = True
        except Exception as e:
            if e.errno == 111 and \
                    self.connection_count < 1 or \
                    re.search(r'operation timed out', e.message) and \
                    self.connection_count < 1:
                self.connection_count += 1
                self.ssl, self.tcp_socket = self.ssl_init()
                self._connect()
            else:
                return(self._error_handler(e))
        if connected:
            return self._write()

    def _error_handler(self, e):
        if e.strerror:
            self.error = e.strerror
        else:
            self.error = e.message
        return self.error

    def _write(self):
        try:
            self.tcp_socket.sendall(self.msg)
        except Exception as e:
            if e.message == None and e.errno == 32 and \
                    self.write_count < 1:
                self.write_count += 1
                self._write()
            else:
                self.error = self._error_handler(e)
        return self._read()

    def _read(self):
        try:
            self.read_data = self.tcp_socket.recv(1024)
        except Exception as e:
            self.error = self._error_handler(e)


    def _close(self):
        tcp_socket.shutdown(socket.SHUT_RDWR)
        tcp_socket.close()

