import re
import sys
import gevent
import ssl
import socket
import select
#from gevent import ssl, socket

class TcpConnect():
    """
    Connect to the remote agent, using the openssl
    library backed by Gevent.
    """
    def __init__(self, host, msg, port=9003, secure=True):
        self.secure = secure
        self.host = host
        self.msg = msg
        self.port = port
        self.connection_count = 0
        self.write_connection_count = 0
        self.write_count = 0
        self.retry = 1
        self.timeout = 30
        self.error = None
        self.read_data = None
        self.key = "/opt/TopPatch/var/lib/ssl/server/keys/server.key"
        self.cert = "/opt/TopPatch/var/lib/ssl/server/keys/server.cert"
        self.ca = "/opt/TopPatch/var/lib/ssl/server/keys/server.cert"
        self.tcp_socket = self.socket_init()
        self._connect()

    def socket_init(self):
        new_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.secure:
            new_wrapper = ssl.SSLSocket(new_socket,
                    keyfile=self.key, certfile=self.cert, ca_certs=self.ca,
                    cert_reqs=ssl.CERT_REQUIRED)
            new_wrapper.timeout = self.timeout
            return new_wrapper
        else:
            #new_socket.timeout = self.timeout
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
                self.tcp_socket = self.socket_init()
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
        read_ready, write_ready, error = select.select([], [self.tcp_socket], [self.tcp_socket], 60)
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

    def _read(self):
        read_ready, write_ready, error = select.select([self.tcp_socket], [], [self.tcp_socket], 30)
        if read_ready:
            print read_ready, error, self.msg
            try:
                self.read_data = self.tcp_socket.recv(1024)
            except Exception as e:
                self.error = self._error_handler(e)
        else:
            self.error = self._error_handler(error)


    def _close(self):
        tcp_socket.shutdown(socket.SHUT_RDWR)
        tcp_socket.close()

