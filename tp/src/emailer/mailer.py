import os
import logging, logging.config
import smtplib
import ConfigParser
from ConfigParser import SafeConfigParser
from utils.common import *
from db.client import *
from db.query_table import *


CONFIG_DIR = '/opt/TopPatch/tp/src/emailer/'
CONFIG_FILE = 'mail.config'
HOST_SECTION = 'host_config'
CREDS_SECTION = 'host_credentials'
logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

def cycle_validator(cycle):
    valid = True
    cycles = cycle.split(" ")
    for i in cycles:
        if not re.search(r'(^[0-9]+)(h|m|s)', i):
            valid = False
    return valid


def create_mail_config(server=None,username=None, password=None,
                port=25, is_tls=False, is_ssl=False,
                from_email=None, to_email=[]
                ):
    CONFIG = CONFIG_DIR + CONFIG_FILE
    if server and username and password \
            and port and from_email and len(to_email) >0:
        if os.path.exists(CONFIG):
            now = datetime.today()
            right_now = '%s_%s_%s_%s_%s_%s' % \
                (now.year, now.month, now.day,
                now.hour, now.minute, now.second)
            BACKUP_CONFIG = CONFIG_DIR + 'mail-%s.config' % (right_now) 
            os.rename(self.CONFIG_FILE, self.BACKUP_CONFIG_FILE)
        to_email = ','.join(to_email)
        Config = ConfigParser.ConfigParser()
        Config.add_section(HOST_SECTION)
        Config.set(HOST_SECTION, 'server', server)
        Config.set(HOST_SECTION, 'port', port)
        Config.set(HOST_SECTION, 'from_email', from_email)
        Config.set(HOST_SECTION, 'to_email', to_email)
        Config.set(HOST_SECTION, 'is_tls', is_tls)
        Config.set(HOST_SECTION, 'is_ssl', is_ssl)
        Config.add_section(CREDS_SECTION)
        Config.set(CREDS_SECTION, 'username', username)
        Config.set(CREDS_SECTION, 'password', password)
        logfile = open(CONFIG, 'w')
        Config.write(logfile)
        logfile.close()



class MailClient():
    def __init__(self, config_file=None):
        self.CONFIG = None
        self.validated = False
        self.connected = False
        self.error = None
        if config_file:
            self.CONFIG = config_file
        else:
            self.CONFIG = CONFIG_DIR + CONFIG_FILE
        if os.path.exists(self.CONFIG):
            self.validated, self.error, creds = self._validate_config_file()
        else:     
            logger.error('Missing config file %s', self.CONFIG)
        if self.validated:
            self.server = creds[0]
            self.username = creds[1]
            self.password = creds[2]
            self.port = creds[3]
            self.from_email = creds[4]
            self.to_email = creds[5].split(",")
            self.is_tls = creds[6]
            self.is_ssl = creds[7]
        else:
            self.server = None
            self.username = None
            self.password = None
            self.port = None
            self.from_email = None
            self.to_email = None
            self.is_tls = None
            self.is_ssl = None


    def connect(self):
        connected = False
        logged_in = False
        msg = None
        mail = None
        try:
            if self.is_ssl:
                mail = smtplib.SMTP_SSL(self.server, self.port, timeout=5)
            else:
                mail = smtplib.SMTP(self.server, self.port, timeout=5)
            connected = True
        except Exception as e:
            logger.error(e)
            msg = e
        if connected:
            try:
                if self.is_tls:
                    mail.starttls()
                mail.login(self.username, self.password)
                logged_in = True
            except Exception as e:
                logger.error(e)
                msg = e
        self.connected = connected
        self.error = msg
        self.logged_in = logged_in
        self.mail = mail
        return(connected, msg, logged_in, mail)


    def _validate_config_file(self):
            reader = SafeConfigParser()
            validated = True
            msg = None
            try:
                reader.read(self.CONFIG)
            except Exception as e:
                logger.error(e)
                validated = False
                return(validated, msg, [])
            if reader.has_section(HOST_SECTION) and \
                reader.has_section(CREDS_SECTION):
                if reader.has_option(HOST_SECTION, 'server'):
                    server = reader.get(HOST_SECTION, 'server')
                else:
                    validated = False
                    msg = 'Missing server option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(HOST_SECTION, 'port'):
                    port = reader.get(HOST_SECTION, 'port')
                else:
                    validated = False
                    msg = 'Missing port option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(HOST_SECTION, 'from_email'):
                    from_email = reader.get(HOST_SECTION, 'from_email')
                else:
                    validated = False
                    msg = 'Missing from_email option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(HOST_SECTION, 'to_email'):
                    to_email = reader.get(HOST_SECTION, 'to_email')
                else:
                    validated = False
                    msg = 'Missing to_email option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(HOST_SECTION, 'is_tls'):
                    is_tls = return_bool(reader.get(HOST_SECTION, 'is_tls'))
                else:
                    validated = False
                    msg = 'Missing is_tls option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(HOST_SECTION, 'is_ssl'):
                    is_ssl = return_bool(reader.get(HOST_SECTION, 'is_ssl'))
                else:
                    validated = False
                    msg = 'Missing is_ssl option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(CREDS_SECTION, 'username'):
                    username = reader.get(CREDS_SECTION, 'username')
                else:
                    validated = False
                    msg = 'Missing username option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(CREDS_SECTION, 'password'):
                    password = reader.get(CREDS_SECTION, 'password')
                else:
                    validated = False
                    msg = 'Missing password option'
                    logger.error(msg)
                    return(validated, msg, [])
            else: 
                validated = False
                msg = 'Missing config section'
                logger.error(msg)
                return(validated, msg, [])
            if validated:
                return(validated, msg, [server, username, password, port, 
                        from_email, to_email, is_tls, is_ssl])
            else:
                return(validated, msg, [])
