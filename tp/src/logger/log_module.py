import os
import socket
import logging
import logging.config
import logging.handlers

logger = logging.getLogger('TopPatch')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filename='/opt/TopPatch/var/log/tp.log'
        
fh = logging.FileHandler(filename, mode='a',encoding=None, delay=False)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

sh = logging.handlers.SysLogHandler(address=('184.72.215.102',514), socktype=socket.SOCK_DGRAM)
sh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(sh)
