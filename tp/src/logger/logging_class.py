import os
import logging
import logging.config
import logging.handlers

class TopPatchLogger():
    logger = logging.getLogger('TopPatch')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def log_to_file(self):
        filename='/opt/TopPatch/var/log/tp.log'
        fh = logging.RotatingFileHandler(filename, mode='a',maxBytes=1000,backupCount=3,encoding=None, delay=False)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info('started logging in %s' % (LOG_FILE))

    def remote_log(self):
        sh = logging.sysLogHandler(address=('localhost', 514), facility=LOG_USER, socktype=socket.SOCK_DGRAM)
        sh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(sh)
