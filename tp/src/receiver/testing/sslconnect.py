import re
import socket
import ssl

class SslConnect():
    def __init__(self, host, msg):
        self.host = host
        self.msg = msg
        self.port = 9000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(60)
        self.connection_count = 0
        self.write_count = 0
        self.retry = 1
        self.connection_error = None
        self.write_error = None
        self.read_error = None
        self.read_data = None
        self.key = "/opt/TopPatch/var/lib/ssl/server/keys/server.key"
        self.cert = "/opt/TopPatch/var/lib/ssl/server/keys/server.cert"
        self.ca = "/opt/TopPatch/var/lib/ssl/server/keys/server.cert"
        self.ssl_socket = ssl.wrap_socket(self.socket,
                keyfile=self.key, certfile=self.cert, ca_certs=self.ca,
                cert_reqs=ssl.CERT_REQUIRED)
        self._connect()


    def _connect(self):
        self.connection_error = None
        try:
            connect = self.ssl_socket.connect((self.host, self.port))
        except Exception as e:
            if e.message == None and e.errno == 111 and \
                    self.connection_count < 1 or \
                    re.search(r'operation timed out', e.message) and \
                    self.connection_count < 1:
                self.connection_count += 1
                self._connect
            else:
                self.error = e
        return self._write()

    def _write(self):
        self.write_error = None
        try:
            written = self.ssl_socket.sendall(self.msg)
        except Exception as e:
            if e.message == None and e.errno == 32 and \
                    self.write_count < 1:
                self.write_count += 1
                self._write()
            else:
                print e.message
                self.error = e.message
        return self._read()

    def _read(self):
        self.read_error = None
        try:
            self.read_data = self.ssl_socket.recv(1024)
        except Exception as e:
            self.read_error = e.message


    def _close(self):
        ssl_socket.shutdown(socket.SHUT_RDWR)
        ssl_socket.close()
