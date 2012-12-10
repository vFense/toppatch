from socket import SOCK_DGRAM, SOCK_STREAM
import socket, sys, struct
import logging
import logging.config
import ConfigParser

class RvLogger():
    def __init__(self):
        self.rproto = {
                'UDP': 'handlers.socket.SOCK_DGRAM',
                'TCP': 'handlers.socket.SOCK_STREAM'
                }
        self.CONFDIR = '/opt/TopPatch/tp/src/logger/'
        self.NEWCONFIG = CONFIDIR+'logging_new.config'
        self.CONFIG = CONFDIR+'logging.config'
        self.level = {
                 'CRITICAL': CRITICAL,
                 'ERROR': ERROR,
                 'WARN': WARN,
                 'INFO': INFO,
                 'DEBUG': DEBUG,
                 }

    def create_config(self, loglevel='INFO',
            loghost=None, logport=None, logproto=None):
        self.Config = ConfigParser.ConfigParser()
        self.loggers = ['root', 'rvlistener', 'rvweb', 'csrlistener']
        self.handlers = ['root', 'rvlist_file', 'rvweb_file', 'csrlist_file']
        self.formatters = ['default'] 
        self.section_logger_name = 'loggers'
        self.section_handler_name = 'handlers'
        self.section_formatters_name = 'formatters'

    def create_logger_list_section(self, additional_loggers=[]):
        if len(additionalloggers) > 0:
            self.loggers = self.loggers + additionalloggers
        self.Config.add_section(self.section_logger_name)
        self.Config.set(section_name, 'key', self.loggers)


    def create_handler_list_section(self, additionalhandlers=[]):
        if len(additionalhandlers) > 0:
            self.handlers = self.handlers + additionalhandlers
        self.Config.add_section(self.section_handler_name)
        self.Config.set(section_name, 'key', self.handlers)


    def create_formatter_list_section(self, additionalformatters=[]):
        if len(additionalformatters) > 0:
            self.formatters = self.formatters + additionalformatters
        self.Config.add_section(self.section_formatters_name)
        self.Config.set(section_name, 'key', self.formatters)

    def create_app_logger(self):

def create_new_log_config(level='INFO', host=None, port=None, proto=None):
    msg = ""
    newfile = open(NEWCONFIG, 'w')
    newfile.write('[loggers]\n')
    newfile.write('keys=root,rvlistener,rvweb,csrlistener\n\n')
    newfile.write('[handlers]\n')
    newfile.write('keys=hand01,rvlist_file,rvweb_file,csrlist_file,syslog\n\n')
    newfile.write('[formatters]\n')
    newfile.write('keys=default\n\n')
    newfile.write('[logger_root]\n')
    newfile.write('level=NOTSET\n')
    newfile.write('handlers=hand01\n')
    newfile.write('qualname=root\n')
    newfile.write('propagate=0\n\n')
    newfile.write('[logger_rvlistener]\n')
    newfile.write('level=INFO\n')
    newfile.write('propagate=0\n')
    newfile.write('qualname=rvlistener\n')
    newfile.write('handlers=rvlist_file,syslog\n\n')
    newfile.write('[logger_rvweb]\n')
    newfile.write('level=INFO\n')
    newfile.write('propagate=0\n')
    newfile.write('qualname=rvweb\n')
    newfile.write('handlers=rvweb_file,syslog\n\n')
    newfile.write('[logger_csrlistener]\n')
    newfile.write('level=INFO\n')
    newfile.write('propagate=0\n')
    newfile.write('qualname=csrlistener\n')
    newfile.write('handlers=csrlist_file,syslog\n\n')
    newfile.write('[handler_hand01]\n')
    newfile.write('class=StreamHandler\n')
    newfile.write('level=NOTSET\n')
    newfile.write('formatter=default\n')
    newfile.write('args=(sys.stdout,)\n')
    newfile.write('stream=sys.stdout\n\n')
    newfile.write('[handler_rvlist_file]\n')
    newfile.write('class=handlers.TimedRotatingFileHandler\n')
    newfile.write('interval=midnight\n')
    newfile.write('backupCount=5\n')
    newfile.write('formatter=default\n')
    newfile.write('level=INFO\n')
    newfile.write('args=("/opt/TopPatch/var/log/rvlistener.log",)\n\n')
    newfile.write('[handler_rvweb_file]\n')
    newfile.write('class=handlers.TimedRotatingFileHandler\n')
    newfile.write('interval=midnight\n')
    newfile.write('backupCount=5\n')
    newfile.write('formatter=default\n')
    newfile.write('level=INFO\n')
    newfile.write('args=("/opt/TopPatch/var/log/rvweb.log",)\n\n')
    newfile.write('[handler_csrlist_file]\n')
    newfile.write('class=handlers.TimedRotatingFileHandler\n')
    newfile.write('interval=midnight\n')
    newfile.write('backupCount=5\n')
    newfile.write('formatter=default\n')
    newfile.write('level=INFO\n')
    newfile.write('args=("/opt/TopPatch/var/log/csrlistener.log",)\n\n')
    newfile.write('[handler_syslog]\n')
    newfile.write('class=handlers.SysLogHandler\n')
    newfile.write('level=ERROR\n')
    newfile.write('formatter=form05\n')
    newfile.write('args=(("'+host+'", '+port+'),handlers.SysLogHandler.LOG_USER, '+str(rproto[proto])+')\n')
    newfile.write('facility=LOG_USER\n\n')
    newfile.write('[formatter_default]\n')
    newfile.write('format=%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
    newfile.write('datefmt=\n')
    newfile.close()

def send_new_logging_config():
    msg = open(FILE, 'r').read()
    t = logging.config.listen(9999)
    t.start()
    HOST = 'localhost'
    PORT = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('connecting...')
    s.connect((HOST, PORT))
    print('sending config...')
    s.send(struct.pack('>L', len(msg)))
    s.send(msg)
    print "finished sending the message"
    s.close()
    print('complete')
    try:
        logging.config.stopListening()
        t.join()
    except Exception as e:
        print dir(e), e
