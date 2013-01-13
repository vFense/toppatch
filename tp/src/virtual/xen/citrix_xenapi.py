import os
import logging, logging.config
import ConfigParser
from ConfigParser import SafeConfigParser
import XenAPI
from db.client import *
from db.query_table import *


CONFIG_DIR = '/opt/TopPatch/tp/src/virtual/xen/'
CONFIG_FILE = 'xen.config'
HOST_SECTION = 'xen_host'
CREDS_SECTION = 'xen_credentials'
OPTIONS = 'options'
HOSTS = 'hosts'
logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

def cycle_validator(cycle):
    valid = True
    cycles = cycle.split(" ")
    for i in cycles:
        if not re.search(r'(^[0-9]+)(h|m|s)', i):
            valid = False
    return valid


def create_xen_config(credentials=None):
    CONFIG = CONFIG_DIR + CONFIG_FILE
    number_of_hosts = None
    count = 1
    if type(credentials) == list and len(credentials) >0 \
            and type(credentials[0]) == dict:
        if os.path.exists(CONFIG):
            now = datetime.today()
            right_now = '%s_%s_%s_%s_%s_%s' % \
                (now.year, now.month, now.day,
                now.hour, now.minute, now.second)
            BACKUP_CONFIG = CONFIG_DIR + 'visdk-%s.config' % (right_now) 
            os.rename(CONFIG, BACKUP_CONFIG)
        number_of_hosts = len(credentials)
        Config = ConfigParser.ConfigParser()
        for creds in credentials:
            if creds['server'] and creds['username'] and creds['password']:
                host_section = HOST_SECTION + '_%s' % (str(count))
                creds_section = CREDS_SECTION + '_%s' % (str(count))
                options = OPTIONS + '_%s' % (str(count))
                Config.add_section(host_section)
                Config.set(host_section, 'server', creds['server'])
                Config.add_section(creds_section)
                Config.set(creds_section, 'username', creds['username'])
                Config.set(creds_section, 'password', creds['password'])
                Config.add_section(options)
                Config.set(options, 'create_snapshot_before_patch', creds['create_snapshot_before_patch'])
                Config.set(options, 'cycle_connect_time', creds['cycle'])
                count = count + 1
        Config.add_section(HOSTS)
        Config.set(HOSTS, 'host_count', number_of_hosts)
        logfile = open(CONFIG, 'w')
        Config.write(logfile)
        logfile.close()


def get_snapshots_for_vm(session, node_id=None, username='system_user'):
        session = validate_session(session)
        snaps = []
        message = None
        passed = True
        if node_id:
            snapshots = snapshots_exist(session, node_id=node_id)
            if len(snapshots) >0:
                for snap in snapshots:
                    snaps.append({
                        'snap_name': snap.name,
                        'snap_description': snap.description,
                        'snap_order': snap.order,
                        'created_time': snap.created_time.\
                                strftime('%m/%d/%Y %H:%M')
                        })
            else:
                message= 'Snapshots do not exist for %s'
                passed = False
        else:
            message= 'Insufficient arguments'
            passed = False
        if passed:
            return(snaps)
        else:
            return({
                'pass': passed,
                'message': message
                })


class XenApi():
    def __init__(self, host=None, config_file=None, username='system_user'):
        self.CONFIG = None
        self.validated = False
        self.connected = False
        self.error = None
        self.config_exists = None
        self.xen_host = host
        if config_file:
            self.CONFIG = config_file
        else:
            self.CONFIG = CONFIG_DIR + CONFIG_FILE
        if os.path.exists(self.CONFIG):
            self.config_exists = True
        else:
            self.config_exists = False
        if self.config_exists and not host:
            self.validated, self.error, self.servers = \
                    self._get_and_validate_config()
        elif self.config_exists and host:
            self.validated, self.error, self.server = \
                    self._get_and_validate_config()
        else:
            msg = 'Missing config file %s' % (self.CONFIG)
            self.error = msg
            logger.error(msg)


    def connect(self, user_name, password):
        connected = False
        logged_in = False
        msg = None
        xen = None
        try:
            xen = XenAPI.Session(self.xen_host)
            connected = True
        except Exception as e:
            logger.error(e)
            msg = e
        if connected:
            try:
                xen.xenapi.login_with_password(user_name, password)
                logged_in = True
            except Exception as e:
                logger.error(e)
                msg = e
        self.connected = connected
        self.error = msg
        self.logged_in = logged_in
        self.xen = xen
        return(connected, msg, logged_in, xen)


    def _get_and_validate_config(self, all_hosts=True, host=None):
            reader = SafeConfigParser()
            validated = True
            hosts = {}
            try:
                reader.read(self.CONFIG)
            except Exception as e:
                msg = e
                logger.error(e)
                return(validated, msg, [])
            count = 1
            host_section = HOST_SECTION + '_%s' % (str(count))
            creds_section = CREDS_SECTION + '_%s' % (str(count))
            options = OPTIONS + '_%s' % (str(count))
            if reader.has_section(host_section) and \
                reader.has_section(creds_section) and \
                reader.has_section(options) and \
                reader.has_section(HOSTS):
                if reader.has_option(HOSTS, 'host_count'):
                    host_count = int(reader.get(HOSTS, 'host_count'))
                    while count <= host_count:
                        if reader.has_option(host_section, 'server'):
                            server = reader.get(host_section, 'server')
                        else:
                            validated = False
                            msg = 'VMWare Missing server option'
                            logger.error(msg)
                            return(validated, msg, [])

                        if reader.has_option(creds_section, 'username'):
                            username = reader.get(creds_section, 'username')
                        else:
                            validated = False
                            msg = 'VMWare Missing username option'
                            logger.error(msg)
                            return(validated, msg, [])

                        if reader.has_option(creds_section, 'password'):
                            password = reader.get(creds_section, 'password')
                        else:
                            validated = False
                            msg = 'VMWare Missing password option'
                            logger.error(msg)
                            return(validated, msg, [])

                        if reader.has_option(options, 'create_snapshot_before_patch'):
                            snapshot_before_patch = reader.get(options,
                                'create_snapshot_before_patch')
                        else:
                            validated = False
                            msg = 'VMWare Missing create_snapshot option'
                            logger.error(msg)
                            return(validated, msg, [])

                        if reader.has_option(options, 'cycle_connect_time'):
                            cycle = reader.get(options,
                                'cycle_connect_time')
                        else:
                            validated = False
                            msg = 'VMWare Missing create_snapshot option'
                            logger.error(msg)
                            return(validated, msg, [])

                        if validated:
                            hosts[server] = {
                                    'server': server,
                                    'username': username,
                                    'password': password,
                                    'create_snapshot_before_patch': snapshot_before_patch,
                                    'cycle': cycle
                                    }
                            if host == server:
                                msg = 'Xen Config was validated'
                                return(validated, msg, hosts)

                        count = count + 1
                        host_section = HOST_SECTION + '_%s' % (str(count))
                        creds_section = CREDS_SECTION + '_%s' % (str(count))
                        options = OPTIONS + '_%s' % (str(count))
            else: 
                validated = False
                msg = 'Missing config section'
                logger.error(msg)
                return(validated, msg, [])
            if validated and all_hosts:
                msg = 'Xen Config was validated'
                logger.info(msg)
                return(validated, msg, hosts)
            else:
                msg = 'Xen Config was not validated'
                logger.error(msg)
                return(validated, msg, [])
