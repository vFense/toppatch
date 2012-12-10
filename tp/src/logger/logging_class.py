import os
#import logging
#import logging.config
#import logging.handlers
from socket import SOCK_DGRAM, SOCK_STREAM
from logging import *


LOGDIR = '/opt/TopPatch/var/log/'
level = {
         'CRITICAL': CRITICAL,
         'ERROR': ERROR,
         'WARN': WARN,
         'INFO': INFO,
         'DEBUG': DEBUG,
        }
rproto = {
         'TCP': SOCK_STREAM,
         'UDP': SOCK_DGRAM,
         }


class TopPatchLogger():
    def __init__(self, appname='TopPatch', loglevel='DEBUG'):
        self.appname = appname
        self.loglevel = loglevel
        logger = getLogger(self.appname)
        logger.setLevel(level[self.loglevel])
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def log_to_file(self, appname=self.appname ):
        filename= LOGDIR = self.appname + '.log'
        fh = logging.RotatingFileHandler(filename, mode='a',maxBytes=1000,backupCount=3,encoding=None, delay=False)
        fh.setLevel(level[self.loglevel])
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info('started logging in %s' % (LOG_FILE))

    def remote_log(self, host='localhost', port=514, proto=TCP):
        proto = rproto[proto]
        sh = logging.sysLogHandler(address=(host, port), facility=LOG_USER, socktype=proto)
        sh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(sh)
