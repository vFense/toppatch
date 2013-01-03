import os
import logging, logging.config
import ConfigParser
from ConfigParser import SafeConfigParser
from pyvisdk import Vim
from db.client import *
from db.query_table import *


CONFIG_DIR = '/opt/TopPatch/tp/src/vmware/'
CONFIG_FILE = 'visdk.config'
HOST_SECTION = 'vm_api_host'
CREDS_SECTION = 'vm_credentials'
OPTIONS = 'options'
logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

def cycle_validator(cycle):
    valid = True
    cycles = cycle.split(" ")
    for i in cycles:
        if not re.search(r'(^[0-9]+)(h|m|s)', i):
            valid = False
    return valid


def create_vm_config(server, username, password,
        create_snapshot=False, cycle='12h'):
    CONFIG = CONFIG_DIR + CONFIG_FILE
    if server and username and password:
        if os.path.exists(CONFIG):
            now = datetime.today()
            right_now = '%s_%s_%s_%s_%s_%s' % \
                (now.year, now.month, now.day,
                now.hour, now.minute, now.second)
            BACKUP_CONFIG = CONFIG_DIR + 'visdk-%s.config' % (right_now) 
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


def get_snapshost_for_vm(session, node_id=None, username='system_user'):
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


class VmApi():
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
            if self.validated:
                self.host = creds[0]
                self.username = creds[1]
                self.password = creds[2]
                self.connected, self.error, self.logged_in, \
                        self.vim = self._connect()
        else:
            msg = 'Missing config file %s' % (self.CONFIG)
            self.error = msg
            logger.error(msg)


    def _connect(self):
        connected = False
        logged_in = False
        msg = None
        try:
            vim = Vim(self.host)
            connected = True
        except Exception as e:
            logger.error(e)
            msg = e
            return(connected, msg, logged_in, None)
        if connected:
            try:
                vim.login(self.username, self.password)
                logged_in = True
            except Exception as e:
                logger.error(e)
                msg = e
                return(connected, msg, logged_in, None)
            if logged_in:
                return(connected, msg, logged_in, vim)
            else:
                return(connected, msg, logged_in, None)
        else:
            return(connected, msg, logged_in, None)


    def _validate_config_file(self):
            reader = SafeConfigParser()
            validated = True
            try:
                reader.read(self.CONFIG)
            except Exception as e:
                msg = e
                logger.error(e)
                return(validated, msg, [])
            if reader.has_section(HOST_SECTION) and \
                reader.has_section(CREDS_SECTION):
                if reader.has_option(HOST_SECTION, 'server'):
                    server = reader.get(HOST_SECTION, 'server')
                else:
                    validated = False
                    msg = 'VMWare Missing server option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(CREDS_SECTION, 'username'):
                    username = reader.get(CREDS_SECTION, 'username')
                else:
                    validated = False
                    msg = 'VMWare Missing username option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(CREDS_SECTION, 'password'):
                    password = reader.get(CREDS_SECTION, 'password')
                else:
                    validated = False
                    msg = 'VMWare Missing password option'
                    logger.error(msg)
                    return(validated, msg, [])
            else: 
                validated = False
                msg = 'Missing config section'
                logger.error(msg)
                return(validated, msg, [])
            if validated:
                msg = 'VMWare Config was validated'
                logger.info(msg)
                return(validated, msg, [server, username, password])
            else:
                msg = 'VMWare Config was not validated'
                logger.error(msg)
                return(validated, msg, [])


    def shutdown_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    vm.ShutdownGuest()
                    message = '%s - %s is shutting down' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during shutdown process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def poweroff_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    vm.PowerOffVM_Task()
                    message = '%s - %s is powered off' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during poweroff process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def poweron_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    vm.PowerOnVM_Task()
                    message = '%s - %s is powered on' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during poweron process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def reboot_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    vm.RebootGuest()
                    message = '%s - %s is rebooting' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during reboot process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def reset_vm(self, vm_name=None):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    vm.ResetVM_Task()
                    message = '%s - %s is in the process of a hard reboot'% \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during reboot process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def create_snapshot(self, vm_name=None, snap_name=None,
            memory=False, quiesce=False, snap_description=None,
            username='system_user'):
        message = None
        passed = None
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
                    message = '%s - snapshot %s created on %s'% \
                            (username, snap_name, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - error during snapshot creation:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        return({
            'pass': passed,
            'message': message
            })


    def get_all_snapshots(self, vm_name=None, username='system_user'):
        message = None
        passed = True
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
                    return(snaps)
                else:
                    message = '%s - Snapshots do not exist for %s' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def remove_all_snapshots(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                try:
                    task = vm.RemoveAllSnapshots_Task()
                    message = ' %s - All snapshots on %s have been deleted' %\
                        (username, vm_name)
                    logger.info(message)
                    passed = True
                except Exception as e:
                    message = '%s - Snapshots werent deleted on %s' % \
                            (username, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def remove_snapshot(self, vm_name=None, snap_name=None,
            remove_children=True, username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                if len(vm.snapshot) >0:
                    snapshot_list = vm.snapshot.rootSnapshotList[0]
                    i = 1
                    while snapshot_list:
                        if snap_name == snapshot_list.name:
                            try:
                                snapshot_list.snapshot.\
                                        RemoveSnapshot_Task(remove_children)
                                message = ' %s - snap %s was deleted on %s' %\
                                        (username, snap_name, vm_name)
                                logger.info(message)
                                passed = True
                                if removed_children:
                                    message = '%s - snap %s deleted on %s %s' %\
                                        (username, snap_name, vm_name,
                                            'and all of its children')
                                    logger.info(message)
                                else:
                                    message = ' %s - snap %s was deleted on %s' %\
                                            (username, snap_name, vm_name)
                                    logger.info(message)

                            except Exception as e:
                                message = '%s - %s couldnt be deleted on %s'%\
                                        (username, snap_name, vm_name)
                                logger.error(message)
                                passed = False
                        i = i + 1
                        if len(snapshot_list.childSnapshotList) > 0:
                            snapshot_list = snapshot_list.childSnapshotList[0]
                        else:
                            snapshot_list = None
                else:
                    message = '%s - Snapshots do not exist for %s' % \
                            (username, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def revert_to_snapshot(self, vm_name=None, snap_name=None,
                username='system_user'):
        message = None
        passed = None
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                if len(vm.snapshot) >0:
                    snapshot_list = vm.snapshot.rootSnapshotList[0]
                    i = 1
                    while snapshot_list:
                        if snap_name == snapshot_list.name:
                            try:
                                snapshot_list.snapshot.RevertToSnapshot_Task()
                                message = ' %s - %s was reverted to %s' %\
                                        (username, vm_name, snap_name)
                                logger.info(message)
                                passed = True
                            except Exception as e:
                                message = '%s - %s couldnt revert to %s'%\
                                        (username, vm_name, snap_name)
                                logger.error(message)
                                passed = False
                        i = i + 1
                        if len(snapshot_list.childSnapshotList) > 0:
                            snapshot_list = snapshot_list.childSnapshotList[0]
                        else:
                            snapshot_list = None
                else:
                    message = '%s - Snapshots do not exist for %s' % \
                            (username, vm_name)
                    logger.error(message)
                    passed = False
            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def get_all_vms(self, username='system_user'):
        message = None
        passed = None
        vms = {}
        if not self.vim.loggedin:
            self.vim.relogin()
        try:
            all_vms = self.vim.getVirtualMachines()
            for vm in all_vms:
                if vm.guest.toolsVersionStatus != 'guestToolsNotInstalled' or \
                        vm.guest.toolsVersionStatus != 'guestToolsUnmanaged':
                    vms[vm.name] = {
                            'vm_name': vm.name,
                            'ip_address': vm.guest.ipAddress,
                            'host_name': vm.guest.hostName,
                            'snapshots': self.get_all_snapshots(vm_name=vm.name,
                                                username=username)
                            }
            passed = True
            return(vms)
        except Exception as e:
            passed = False
            message = '%s - couldnt retreive the virtual machines: %s' % \
                    (username, e)
            return({
                'pass': passed,
                'message': message
                })