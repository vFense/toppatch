from datetime import datetime
import re
import logging, logging.config
from ConfigParser import SafeConfigParser
from vmapi import *
from db.client import *
from models.node import *
from models.snapshots import *
from models.virtualization import *

from apscheduler.scheduler import Scheduler

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

tconvert = {
        'h': 'hours',
        'm': 'minutes',
        's': 'seconds'
        }

def parse_interval(interval):
    interval = interval.split(" ")
    interval_time = {}
    for i in interval:
        if re.search(r'(^[0-9]+)(h|m|s)', i):
            key, value = re.search(r'(^[0-9]+)(h|m|s)', i).group(1,2)
            interval_time[tconvert[value]] = int(key)
    return interval_time


CONFIG = CONFIG_DIR + CONFIG_FILE
reader = SafeConfigParser()


def get_vm_data(username='system_user'):
    ENGINE = init_engine()
    session = create_session(ENGINE)
    session = validate_session(session)
    nodes = session.query(NodeInfo).all()
    vm = VmApi()
    vm.connect()
    if vm.logged_in:
        vm_nodes = vm.get_all_vms()
        for node in nodes:
            for key, value in vm_nodes.items():
                match = False
                esx_host = session.query(VirtualHostInfo).\
                    filter(VirtualHostInfo.name == value['esx_host']).first()
                if value['vm_name'] and value['ip_address'] and value['host_name']:
                    if re.search(node.ip_address, value['ip_address']):
                        match = True
                    elif node.host_name:
                        if re.search(node.host_name, value['host_name']):
                            match = True
                    if match:
                        node.is_vm = True
                        vm = session.query(VirtualMachineInfo).\
                                filter(VirtualMachineInfo.node_id 
                                        == node.id).first()
                        if vm and esx_host:
                            vm.virtual_host_id = esx_host.id
                            vm.vm_name = value['vm_name']
                            vm.uuid = value['uuid']
                            vm.tools_status = value['tools_status']
                            vm.tools_version = value['tools_version']
                            try:
                                session.commit()
                            except Exception as e:
                                session.rollback()
                        if not esx_host:
                            esx_host = VirtualHostInfo(
                                    name=value['esx_host'],
                                    version=value['esx_version'],
                                    virt_type=value['esx_name']
                                    )
                            try:
                                session.add(esx_host)
                                session.commit()
                            except Exception as e:
                                session.rollback()

                        if not vm:
                            try:
                                vm_info = VirtualMachineInfo(node_id=node.id,
                                        virtual_host_id=esx_host.id, 
                                        vm_name=value['vm_name'],
                                        uuid=value['uuid'],
                                        tools_status=value['tools_status'],
                                        tools_version=value['tools_version']
                                        )
                                session.add(vm_info)
                                session.commit()
                            except Exception as e:
                                session.rollback()

                        snapshots = session.query(SnapshotsPerNode).\
                            filter(SnapshotsPerNode.node_id == node.id).all()
                        if len(snapshots) >0:
                            for snap in snapshots:
                                try:
                                    session.delete(snap)
                                    session.commit()
                                    message = '%s - Snapshot %s deleted' % \
                                            (username, snap.name)
                                    logger.info(message)
                                except Exception as e:
                                    session.rollback()
                                    passed = False
                                    message = '%s - Couldnt delete Snapshot %s' % \
                                            (username, snap.name)
                                    logger.error(message)
                        if len(value['snapshots']) >0:
                            for snaps in value['snapshots'].values():
                                if type(snaps) == dict:
                       	            snap = SnapshotsPerNode(node_id=node.id,
                                        name=snaps['name'],
                                        description=snaps['description'],
                                        order=int(snaps['order_id']),
                                        created_time=snaps['created']
                                        )
                                    try:
                                        session.add(snap)
                                        session.commit()
                                        message = '%s - Snapshot %s added into RV' % \
                                            (username, snaps['name'])
                                        logger.info(message)
                                        passed = True
                                    except Exception as e:
                                        session.rollback()
                                        passed = False
                                        message = '%s - Couldnt add snapshot %s' % \
                                            (username, snaps['name'])
                                        logger.error(message)

                    if not match:
                        next
    else:
        logger.error('%s - Can not log into VMHost' % (username))
    session.close()
