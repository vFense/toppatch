import os
import logging, logging.config
import ConfigParser
from ConfigParser import SafeConfigParser
from pyvisdk import Vim


CONFIG_DIR = '/opt/TopPatch/tp/src/vmware/'
CONFIG_FILE = 'visdk.config'
HOST_SECTION = 'vm_api_host'
CREDS_SECTION = 'vm_credentials'
OPTIONS = 'options'

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

def create_vm_config(server, username, password,
        create_snapshot=False, cycle='3h'):
    CONFIG = CONFIG_DIR + CONFIG_FILE
    if server and username and password:
        if os.path.exists(CONFIG):
            now = datetime.today()
            right_now = '%s_%s_%s_%s_%s_%s' % \
                (now.year, now.month, now.day,
                now.hour, now.minute, now.second)
            BACKUP_CONFIG = CONFIG_DIR + 'logging-%s.config' % (right_now) 
            os.rename(self.CONFIG_FILE, self.BACKUP_CONFIG_FILE)
        Config = ConfigParser.ConfigParser()
        Config.add_section(HOST_SECTION)
        Config.set(HOST_SECTION, 'server', server)
        Config.add_section(CREDS_SECTION)
        Config.set(CREDS_SECTION, 'username', username)
        Config.set(CREDS_SECTION, 'password', password)
        Config.add_section(OPTIONS)
        Config.set(OPTIONS, 'create_snapshot_before_patch', create_snapshot)
        Config.set(OPTIONS, 'cycle_connect_time', cycle)
        logfile = open(CONFIG, 'w')
        Config.write(logfile)
        logfile.close()


class vmapi():
    def __init__(self, config_file=None):
        self.CONFIG = None
        self.validated = False
        self.connected = False
        if config_file:
            self.CONFIG = config_file
        else:
            self.CONFIG = CONFIG_DIR + CONFIG_FILE
        if os.path.exists(self.CONFIG):
            self.validated, creds = self._validate_config_file()
            self.host = creds[0]
            self.username = creds[1]
            self.password = creds[2]
            self.connected, self.logged_in, self.vim = self._connect()
        else:     
            logger.error('Missing config file %s', self.CONFIG)

    def _connect(self):
        connected = False
        logged_in = False
        try:
            vim = Vim(self.host)
            connected = True
        except Exception as e:
            logger.error(e)
        if connected:
            try:
                vim.login(self.username, self.password)
                logged_in = True
            except Exception as e:
                logger.error(e)
            if logged_in:
                return(connected, logged_in, vim)
            else:
                return(connected, logged_in, None)
        else:
            return(connected, logged_in, None)


    def _validate_config_file(self):
            reader = SafeConfigParser()
            validated = True
            try:
                reader.read(self.CONFIG)
            except Exception as e:
                print e
            if reader.has_section(HOST_SECTION) and \
                reader.has_section(CREDS_SECTION):
                if reader.has_option(HOST_SECTION, 'server'):
                    server = reader.get(HOST_SECTION, 'server')
                else:
                    validated = False
                    logger.error('Missing server option')
                if reader.has_option(CREDS_SECTION, 'username'):
                    username = reader.get(CREDS_SECTION, 'username')
                else:
                    validated = False
                    logger.error('Missing username option')
                if reader.has_option(CREDS_SECTION, 'password'):
                    password = reader.get(CREDS_SECTION, 'password')
                else:
                    validated = False
                    logger.error('Missing password option')
            else: 
                validated = False
                logger.error('Missing config sections')
            if validated:
                return(validated, [server, username, password])
            else:
                return(validated, [])


    def create_snapshot(self, vm_name=None, snap_name=None,
            memory=True, quiesce=True, snap_description=None):
            if not self.vim.loggedin:
                self.vim.relogin()
            if vm_name and snap_name:
                if not snap_description:
                    snap_description = snap_name
                vm = self.vim.getVirtualMachine(vm_name)
                if vm:
                    try:
                        snap = vm.CreateSnapshot_Task(snap_name, memory,
                                quiesce, snap_description)
                        logger.info('%s created for %s' % \
                            (snap_name, vm_name)
                            )
                    except Exception as e:
                        logger.error(e)
                else:
                    logger.error('VM by the name of %s does not exist' % \
                            (vm_name)
                            )
            else:
                logger.error('insufficient parameters')


    def get_all_snapshots(self, vm_name=None):
        snaps = {}
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                if len(vm.snapshot) >0:
                    snapshot_list = vm.snapshot.rootSnapshotList[0]
                    i = 1
                    while snapshot_list:
                        snaps[snapshot_list.name] = {
                                'name': snapshot_list.name,
                                'created': snapshot_list.createTime,
                                'description': snapshot_list.description,
                                'order_id': i
                                }
                        i = i + 1
                        if len(snapshot_list.childSnapshotList) > 0:
                            snapshot_list = snapshot_list.childSnapshotList[0]
                        else:
                            snapshot_list = None
                    print snaps
                else:
                    logger.info('Snapshots do not exist for %s' % vm_name)
            else:
                logger.error('VM by the name of %s does not exist' % \
                        (vm_name)
                        )
        else:
            logger.error('insufficient parameters')


    def remove_all_snapshots(self, vm_name=None):
        snaps = {}
        if not vim.loggedin:
            vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                task = vm.RemoveAllSnapshots_Task()
                logger.info('All snapshots on %s have been deleted' %
                        (vm_name)
                        )
            else:
                logger.error('VM by the name of %s does not exist' % \
                        (vm_name)
                        )
