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
                 'CRITICAL': 'CRITICAL',
                 'ERROR': 'ERROR',
                 'WARN': 'WARN',
                 'INFO': 'INFO',
                 'DEBUG': 'DEBUG',
                 }

    def create_config(self, loglevel='INFO', LOGDIR='/opt/TopPatch/var/log/',
            loghost=None, logport=None, logproto=None):
        try:
            self.loglevel = self.level[loglevel]
        execpt Exception as e:
            print 'incorrect level %s ' % (loglevel)
            print 'acceptable levels are %s' % (",".join(self.level.values())
        self.Config = ConfigParser.ConfigParser()
        self.logdir = LOGDIR
        self.loggers = ['root', 'rvlistener', 'rvweb', 'csrlistener']
        self.handlers = ['root', 'rvlist_file', 'rvweb_file', 'csrlist_file']
        self.formatters = ['default'] 
        self.section_logger_name = 'loggers'
        self.section_handler_name = 'handlers'
        self.section_formatters_name = 'formatters'
        self.syslog = None
        if loghost:
            self.syslog = 'syslog_'+loghost
            self.loggers.append(self.syslog)
            self.handlers.append(self.syslog)
        self.logger_handler = zip(self.loggers, self.handlers)

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

    def create_logger_settings(self):
        default_name = 'logger_'
        for name in self.logger_handler:
            app_name = default_name + name[0]
            handlers = [app_name]
            self.Config.add_section(app_name)
            if self.syslog:
                handlers.append(self.syslog)
            self.Config.set(app_name, 'level', self.loglevel)
            self.Config.set(app_name, 'propagate', '0')
            self.Config.set(app_name, 'qualname', app_name)
            self.Config.set(app_name, 'handlers', handlers)


    def create_handler_settings(self):
        default_name = 'handler_'
        for name in self.logger_handler:
            handler_name = default_name + name[1]
            handlers = [handler_name]
            self.Config.add_section(handler_name)
            if self.syslog:
                handlers.append(self.syslog)
            if re.search(r'root', name[1]):
                self.Config.set(handler_name, 'class',
                        'StreamHandler')
                self.Config.set(handler_name, 'stream',
                        'sys.stdout')
                self.Config.set(handler_name, 'args',
                        '(sys.stdout,)')
            elif re.search(r'syslog', name[1]):
                self.Config.set(handler_name, 'class',
                        'handlers.SysLogHandler')
                self.Config.set(handler_name, 'args',
                        'handlers.SysLogHandler')
            else:
                logfile = '("'+ self.logdir + handler_name + '.log,")'
                self.Config.set(handler_name, 'class',
                        'handlers.TimedRotatingFileHandler')
                self.Config.set(handler_name, 'interval', 'midnight')
                self.Config.set(handler_name, 'backupCount', '5')
                self.Config.set(handler_name, 'args', logfile)
            self.Config.set(handler_name, 'level', self.loglevel)
            self.Config.set(handler_name, 'formatter', self.formatters)
            self.Config.set(handler_name, 'handlers', handlers)

def create_new_log_config(level='INFO', host=None, port=None, proto=None):
    msg = ""
    newfile = open(NEWCONFIG, 'w')
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
