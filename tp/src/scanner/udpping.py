#!/usr/bin/env python

import os
import sys
import select

from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM



class UdpPing():
    def __init__(self, host=None, port=1, count=1, timeout=.50):
        self.alive = None
        self.failed = 0
        self.passed = 0
        self.host = host
        self.port = port
        self.timeout = timeout
        loopn = 1
        if not host:
            raise NameError("Pass a valid hostname or ip")
        while loopn <= count: 
            udpsocket = socket(AF_INET, SOCK_DGRAM)
            udpsocket.setblocking(0)
            try:
                udpsocket.connect((self.host, self.port))
            except Exception as e:
                raise e.error("Pass a valid hostname or ip")
            udpsocket.sendall('BOO')
            ready = select.select([udpsocket], [], [], self.timeout) # FD, timeout 1
            if ready[0]:
                try:
                    udpsocket.recv(1024)
                except Exception as e:
                    if e.errno == 111:
                        self.alive = True
                        self.passed = self.passed + 1
            else:
                self.alive = False
                self.failed = self.failed + 1
            loopn = loopn + 1


#a = UdpPing("10.0.0.10", count=3, timeout=.40, port=1)
#print a.alive, a.host, a.port, a.passed, a.failed
