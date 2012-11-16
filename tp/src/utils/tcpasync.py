import re
import sys
import gevent
from gevent import monkey
import ssl
import socket
import select

monkey.patch_socket()

class TcpConnect():
    """
    Connect to the remote agent, using the openssl
    library backed by Gevent.
    """
    def __init__(self, host, msg, port=9003, secure=True, timeout=60):
        self.secure = secure
        self.host = host
        self.msg = msg
        self.port = port
        self.connection_count = 0
        self.write_connection_count = 0
        self.write_count = 0
        self.retry = 1
        self.timeout = timeout
        self.error = None
        self.read_data = None
        self.key = "/opt/TopPatch/var/lib/ssl/server/keys/server.key"
        self.cert = "/opt/TopPatch/var/lib/ssl/server/keys/server.cert"
        self.ca = "/opt/TopPatch/var/lib/ssl/server/keys/CA.cert"
        self.tcp_socket = self.socket_init()
        self._connect()

    def socket_init(self):
        new_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.secure:
            new_wrapper = ssl.SSLSocket(new_socket,
                    keyfile=self.key, certfile=self.cert, ca_certs=self.ca,
                    cert_reqs=ssl.CERT_REQUIRED)
            new_wrapper.settimeout(self.timeout)
            return new_wrapper
        else:
            new_socket.settimeout(self.timeout)
            return new_socket

    def _connect(self):
        connected = None
        try:
            self.tcp_socket.connect((self.host, self.port))
            connected = True
        except Exception as e:
            print e
            if e.errno == 111 and \
                    self.connection_count < 1 or \
                    re.search(r'operation timed out', e.message) and \
                    self.connection_count < 1:
                self.connection_count += 1
                self.tcp_socket = self.socket_init()
                self._connect()
            else:
                print e
                return(self._error_handler(e))
        if connected:
            return self._write()

    def _error_handler(self, e):
        print dir(e), e
        if e is None:
            self.error = "Error Undefined"
        elif e.message:
            self.error = e.message
        else:
            self.error = e.strerror
        return self.error

    def _write(self):
        read_ready, write_ready, error = select.select([], [self.tcp_socket], [self.tcp_socket], self.timeout)
        if write_ready:
            try:
                self.tcp_socket.sendall(self.msg)
            except Exception as e:
                if e.message == None and e.errno == 32 and \
                        self.write_count < 1:
                    self.write_count += 1
                    self._write()
                else:
                    self.error = self._error_handler(e)
            if self.secure:
                return self._read()
        else:
            if self.write_connection_count < 1:
                self.write_connection_count +=1
                self.tcp_socket = self.socket_init()
                self._connect()
            else:
                self.error = self._error_handler(error)
                print "writing to socket failed", error

    def _read(self):
        read_ready, write_ready, error = select.select([self.tcp_socket], [], [self.tcp_socket], self.timeout)
        if read_ready:
            try:
                self.read_data = self.tcp_socket.recv(1024)
            except Exception as e:
                print dir(e), e
                self.error = self._error_handler(e)
        else:
            self.error = self._error_handler(error)
            print "reading from socket failed", error


    def _close(self):
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()

