import os
import logging, logging.config
import ConfigParser
from ConfigParser import SafeConfigParser
from pyvisdk import Vim
from db.client import *
from db.query_table import *
from db.update_table import *
from models.virtualization import *
import tornadoredis

redis = tornadoredis.Client()
redis.connect()

CONFIG_DIR = '/opt/TopPatch/conf/'
CONFIG_FILE = 'visdk.config'
HOST_SECTION = 'vm_api_host'
CREDS_SECTION = 'vm_credentials'
OPTIONS = 'options'
logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')
ENGINE = init_engine()

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
            os.rename(CONFIG, BACKUP_CONFIG)
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


def get_vm_info_from_db(session, node_id=None, username='system_user'):
    session = validate_session(session)
    message = None
    passed = True
    if node_id:
        is_vm = session.query(NodeInfo.is_vm).\
                filter(NodeInfo.id == node_id).first()[0]
        if is_vm:
            vm_info = session.query(NodeInfo,\
                    VirtualMachineInfo, VirtualHostInfo).\
                filter(NodeInfo.id == node_id).\
                join(VirtualMachineInfo, VirtualHostInfo).first()
            if vm_info:
                snaps = get_snapshost_for_vm(session, node_id=node_id, username=username)
                if type(snaps) != list:
                    snaps = []
                return({
                    'vm_name': vm_info.VirtualMachineInfo.vm_name,
                    'tools_status': vm_info.VirtualMachineInfo.tools_status,
                    'tools_version': vm_info.VirtualMachineInfo.tools_version,
                    'uuid': vm_info.VirtualMachineInfo.uuid,
                    'hyper_visor_name': vm_info.VirtualHostInfo.name,
                    'hyper_visor_name': vm_info.VirtualHostInfo.name,
                    'hyper_visor_version': vm_info.VirtualHostInfo.version,
                    'hyper_visor_type': vm_info.VirtualHostInfo.virt_type,
                    'hyper_visor_ip': vm_info.VirtualHostInfo.ip_address,
                    'snapshots': snaps
                    })
            else:
                return({
                    'pass': False,
                    'message': 'Node doesnt have any vm_information'
                    })

        else:
            return({
                'pass': False,
                'message': 'Node is not a VM'
                })
    else:
        return({
            'pass': False,
            'message': 'Node is not a VM'
            })


class VmApi():
    def __init__(self, config_file=None):
        self.CONFIG = None
        self.validated = False
        self.connected = False
        self.error = None
        self.config_exists = None
        if config_file:
            self.CONFIG = config_file
        else:
            self.CONFIG = CONFIG_DIR + CONFIG_FILE
        if os.path.exists(self.CONFIG):
            self.config_exists = True
        else:
            self.config_exists = False
        if self.config_exists:
            self.validated, self.error, creds = \
                    self._get_and_validate_config()
            if self.validated:
                self.host = creds[0]
                self.username = creds[1]
                self.password = creds[2]
                self.create_snapshot_before_patch = creds[3]
                self.cycle = creds[4]
            else:
                self.host = None
                self.username = None
                self.password = None
                self.create_snapshot_before_patch = None
                self.cycle = None
        else:
            self.host = None
            self.username = None
            self.password = None
            self.create_snapshot_before_patch = None
            self.cycle = None
            msg = 'Missing config file %s' % (self.CONFIG)
            self.error = msg
            logger.error(msg)


    def connect(self):
        connected = False
        logged_in = False
        msg = None
        vim = None
        try:
            vim = Vim(self.host)
            connected = True
        except Exception as e:
            logger.error(e)
            msg = e
        if connected:
            try:
                vim.login(self.username, self.password)
                logged_in = True
            except Exception as e:
                logger.error(e)
                msg = e
        self.connected = connected
        self.error = msg
        self.logged_in = logged_in
        self.vim = vim
        return(connected, msg, logged_in, vim)


    def _get_and_validate_config(self):
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
                if reader.has_option(OPTIONS, 'create_snapshot_before_patch'):
                    snapshot_before_patch = reader.get(OPTIONS,
                            'create_snapshot_before_patch')
                else:
                    validated = False
                    msg = 'VMWare Missing create_snapshot option'
                    logger.error(msg)
                    return(validated, msg, [])
                if reader.has_option(OPTIONS, 'cycle_connect_time'):
                    cycle = reader.get(OPTIONS,
                            'cycle_connect_time')
                else:
                    validated = False
                    msg = 'VMWare Missing create_snapshot option'
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
                return(validated, msg, [server, username, password,
                        snapshot_before_patch, cycle])
            else:
                msg = 'VMWare Config was not validated'
                logger.error(msg)
                return(validated, msg, [])


    def shutdown_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'shutdown_vm',
                        operation_sent=datetime.now(),
                        operation_received=datetime.now(),
                        username=username)
                try:
                    vm.ShutdownGuest()
                    message = '%s - %s is shutting down' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )

                except Exception as e:
                    message = '%s - error during shutdown process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False

        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        session.close()

        return({
            'pass': passed,
            'message': message
            })


    def poweroff_vm(self, vm_name=None, username='system_user'):
        message = None
        passed = None
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'poweroff_vm',
                        operation_sent=datetime.now(),
                        operation_received=datetime.now(),
                        username=username)
                try:
                    vm.PowerOffVM_Task()
                    message = '%s - %s is powered off' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=True,
                            results_received=datetime.now()
                            )

                except Exception as e:
                    message = '%s - error during poweroff process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False

        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False

        session.close()
        return({
            'pass': passed,
            'message': message
            })


    def poweron_vm(self, vm_name=None, username='system_user'):
        session = create_session(ENGINE)
        message = None
        passed = None
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'poweron_vm',
                        operation_sent=datetime.now(),
                        operation_received=datetime.now(),
                        username=username)
                try:
                    vm.PowerOnVM_Task()
                    message = '%s - %s is powered on' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )

                except Exception as e:
                    message = '%s - error during poweron process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False

        session.close()
        return({
            'pass': passed,
            'message': message
            })


    def reboot_vm(self, vm_name=None, username='system_user'):
        session = create_session(ENGINE)
        message = None
        passed = None
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'reboot_vm',
                        operation_sent=datetime.now(),
                        operation_received=datetime.now(),
                        username=username)
                try:
                    vm.RebootGuest()
                    message = '%s - %s is rebooting' % \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )

                except Exception as e:
                    message = '%s - error during reboot process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False
        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False

        session.close()

        return({
            'pass': passed,
            'message': message
            })


    def reset_vm(self, vm_name=None):
        session = create_session(ENGINE)
        message = None
        passed = None
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'reset_vm',
                        operation_sent=datetime.now(),
                        operation_received=datetime.now(),
                        username=username)
                try:
                    vm.ResetVM_Task()
                    message = '%s - %s is in the process of a hard reboot'% \
                            (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )

                except Exception as e:
                    message = '%s - error during reboot process:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False

        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False

        session.close()
        return({
            'pass': passed,
            'message': message
            })


    def create_snapshot(self, vm_name=None, snap_name=None,
            memory=False, quiesce=False, snap_description=None,
            username='system_user'):
        message = None
        passed = None
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and snap_name and node:
            if not snap_description:
                snap_description = snap_name
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'create_snapshot',
                        operation_sent=datetime.now(), 
                        operation_received=datetime.now(),
                        username=username)
                try:
                    snap = vm.CreateSnapshot_Task(snap_name, memory,
                            quiesce, snap_description)
                    message = '%s - snapshot %s created on %s'% \
                            (username, snap_name, vm_name)
                    logger.info(message)
                    redis.publish('rv', 'snap created')
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )
                    snapshots = self.get_all_snapshots(vm_name=vm_name,
                            username=username)
                    snaps_updated = self.update_snapshots_for_vm(session,
                            vm_name=vm_name, snapshots=snapshots,
                            username=username)

                except Exception as e:
                    message = '%s - error during snapshot creation:%s on %s'% \
                            (username, e, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False

        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False

        session.close()
        return({
            'pass': passed,
            'message': message
            })

    def update_snapshots_for_vm(self, session, vm_name=None, snapshots=None,
            username='system_user'):
        session = validate_session(session)
        snaps_deleted = False
        snaps_updated = True
        if snapshots and vm_name:
            vmnode = session.query(VirtualMachineInfo).\
                    filter(VirtualMachineInfo.vm_name == vm_name).first()
            if vmnode:
                try:
                    session.query(SnapshotsPerNode).\
                            filter(SnapshotsPerNode.node_id == \
                            vmnode.node_id).delete()
                    session.commit()
                    snaps_deleted = True
                except Exception as e:
                    print e, 'failed trying to delete snaps'
                    session.rollback()
                if not 'pass' in snapshots:
                    for snap in snapshots.values():
                        vm_snap = SnapshotsPerNode(node_id=vmnode.node_id,
                                name=snap['name'],
                                description=snap['description'],
                                order=int(snap['order_id']),
                                created_time=snap['created'])
                        try:
                            session.add(vm_snap)
                            session.commit()
                        except Exception as e:
                            print e, 'failed trying to add snaps'
                            session.rollback()
                            snaps_updated = False
                    redis.publish('rv', 'SnapShots Updated')
        session.close()

        return(snaps_updated)


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
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                oper = add_operation(session, node.node_id, 'remove_all_snapshots',
                        operation_sent=datetime.now(), 
                        operation_received=datetime.now(),
                        username=username)
                try:
                    task = vm.RemoveAllSnapshots_Task()
                    message = ' %s - All snapshots on %s have been deleted' %\
                        (username, vm_name)
                    logger.info(message)
                    passed = True
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed,
                            results_received=datetime.now()
                            )
                    redis.publish('rv', message)
                    snapshots = self.get_all_snapshots(vm_name=vm_name,
                            username=username)
                    snaps_updated = self.update_snapshots_for_vm(session,
                            vm_name=vm_name, snapshots=snapshots,
                            username=username)

                except Exception as e:
                    print e
                    message = '%s - Snapshots werent deleted on %s' % \
                            (username, vm_name)
                    logger.error(message)
                    passed = False
                    results = add_results_non_json(session, node_id=node.node_id,
                            oper_id=oper.id, result=passed, error=e,
                            results_received=datetime.now()
                            )

            else:
                message = '%s - VM by the name of %s does not exist' % \
                        (username, vm_name)
                logger.error(message)
                passed = False

        else:
            message = '%s - insufficient parameters' % (username)
            logger.error(message)
            passed = False
        
        session.close()
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def remove_snapshot(self, vm_name=None, snap_name=None,
            remove_children=True, username='system_user'):
        message = None
        passed = None
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                if len(vm.snapshot) >0:
                    snapshot_list = vm.snapshot.rootSnapshotList[0]
                    i = 1
                    oper = add_operation(session, node.node_id, 'remove_snapshot',
                            operation_sent=datetime.now(), 
                            operation_received=datetime.now(),
                            username=username)
                    while snapshot_list:
                        if snap_name == snapshot_list.name:
                            try:
                                snapshot_list.snapshot.\
                                        RemoveSnapshot_Task(remove_children)
                                message = ' %s - snap %s was deleted on %s' %\
                                        (username, snap_name, vm_name)
                                logger.info(message)
                                passed = True
                                if remove_children:
                                    message = '%s - snap %s deleted on %s %s' %\
                                        (username, snap_name, vm_name,
                                            'and all of its children')
                                    logger.info(message)
                                else:
                                    message = ' %s - snap %s was deleted on %s' %\
                                            (username, snap_name, vm_name)
                                    logger.info(message)
                                results = add_results_non_json(session,
                                        node_id=node.node_id, oper_id=oper.id,
                                        result=passed,
                                        results_received=datetime.now()
                                        )

                            except Exception as e:
                                message = '%s - %s couldnt be deleted on %s'%\
                                        (username, snap_name, vm_name)
                                logger.error(message)
                                passed = False
                                results = add_results_non_json(session,
                                        node_id=node.node_id, oper_id=oper.id,
                                        result=passed, error=e,
                                        results_received=datetime.now()
                                        )
                        i = i + 1
                        if len(snapshot_list.childSnapshotList) > 0:
                            snapshot_list = snapshot_list.childSnapshotList[0]
                        else:
                            snapshot_list = None
                    redis.publish('rv', 'snaps deleted')
                    snapshots = self.get_all_snapshots(vm_name=vm_name,
                            username=username)
                    snaps_updated = self.update_snapshots_for_vm(session,
                            vm_name=vm_name, snapshots=snapshots,
                            username=username)
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

        session.close()
        if not passed:
            return({
                'pass': passed,
                'message': message
                })


    def revert_to_snapshot(self, vm_name=None, snap_name=None,
                username='system_user'):
        message = None
        passed = None
        session = create_session(ENGINE)
        node = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.vm_name == vm_name).first()
        if not self.vim.loggedin:
            self.vim.relogin()
        if vm_name and node:
            vm = self.vim.getVirtualMachine(vm_name)
            if vm:
                if len(vm.snapshot) >0:
                    snapshot_list = vm.snapshot.rootSnapshotList[0]
                    i = 1
                    oper = add_operation(session, node.node_id, 'remove_snapshot',
                            operation_sent=datetime.now(),
                            operation_received=datetime.now(),
                            username=username)
                    while snapshot_list:
                        if snap_name == snapshot_list.name:
                            try:
                                snapshot_list.snapshot.RevertToSnapshot_Task()
                                message = ' %s - %s was reverted to %s' %\
                                        (username, vm_name, snap_name)
                                logger.info(message)
                                passed = True
                                results = add_results_non_json(session,
                                        node_id=node.node_id, oper_id=oper.id,
                                        result=passed,
                                        results_received=datetime.now()
                                        )

                            except Exception as e:
                                message = '%s - %s couldnt revert to %s'%\
                                        (username, vm_name, snap_name)
                                logger.error(message)
                                passed = False
                                results = add_results_non_json(session,
                                        node_id=node.node_id, oper_id=oper.id,
                                        result=passed, error=e,
                                        results_received=datetime.now()
                                        )

                        i = i + 1
                        if len(snapshot_list.childSnapshotList) > 0:
                            snapshot_list = snapshot_list.childSnapshotList[0]
                        else:
                            snapshot_list = None
                    snapshots = self.get_all_snapshots(vm_name=vm_name,
                            username=username)
                    snaps_updated = self.update_snapshots_for_vm(session,
                            vm_name=vm_name, snapshots=snapshots,
                            username=username)
                    redis.publish('rv', message)
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

        session.close()
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
                    esx_host = vm.core.getHostSystem()[0]
                    #esx_net = esx_host.config.network.vnic
                    #esx_ip = None
                    #for network in esx_net:
                    #    if 'Management Network' in network.portgroup:
                    #        esx_ip = network.spec.ip.ipAddress
                    ip_list = []
                    ipaddress_list = vm.guest.net
                    for ip in ipaddress_list:
                        if len(ip.ipAddress) >0:
                            if len(ip.ipAddress[0]) <=15:
                            	ip_list.append(ip.ipAddress[0])
                            if len(ip.ipAddress[1]) <=15:
                            	ip_list.append(ip.ipAddress[0])
                    vms[vm.name] = {
                            'vm_name': vm.name,
                            'vm_uuid': vm.name,
                            'ip_address': ip_list,
                            'host_name': vm.guest.hostName,
                            'uuid': vm.config.uuid,
                            'tools_status': vm.guest.toolsVersionStatus,
                            'tools_version': vm.guest.toolsVersion,
                            'snapshots': self.get_all_snapshots(vm_name=vm.name,
                                                username=username),
                            'esx_host': esx_host.summary.config.name,
                            'esx_name': esx_host.summary.config.product.name,
                            'esx_version': esx_host.summary.config.product.version
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
