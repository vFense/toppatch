#!/usr/bin/python
import time
import os
import re

import sys
import argparse

from daemon import runner
sys.path.append(re.sub(r'\/\w+$', '', os.path.dirname(os.path.abspath(__file__))))
from utils.utils import get_networks_to_scan
import pyping


class Scanner():
    def __init__(self, networks=get_networks_to_scan()):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/opt/tmp/scanner.pid'
        self.pidfile_timeout = 5
        print networks
    def run(self):
        while True:
            
            time.sleep(10)

#get_networks_to_scan()
app = Scanner()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
