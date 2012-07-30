#!/usr/bin/python
import time
import os
import re
import sys
import argparse

from daemon import runner
import pyping
from ipaddr import IPv4Network

from utils.utils import *
from udpping import UdpPing

class Scanner():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/opt/tmp/scanner.pid'
        self.pidfile_timeout = 5

    def scan_network(self, networks=[], proto="udp"):
        self.proto = proto
        if not networks:
            self.networks = get_networks_to_scan()
        elif verify_networks(networks)[1] != True:
            raise Exception("Network not in correct format")
        else:
            self.networks = verify_networks(networks)[0]
    
        for network in self.networks:
            net = IPv4Network(network[0])
            for node in net.iterhosts():
                node = str(node)
                if self.proto == "udp":
                    scan = UdpPing(node, timeout=.50)
                    print scan.alive, scan.host, scan.port, scan.passed, scan.failed

    def run(self):
        while True:
            
            time.sleep(10)



#get_networks_to_scan()
#app = Scanner()
app = Scanner()
app.scan_network("192.168.1.6/24")
#daemon_runner = runner.DaemonRunner(app)
#daemon_runner.do_action()
