from datetime import datetime
import re
import logging, logging.config
from ConfigParser import SafeConfigParser
from vmapi import *
from db.client import *
from models.node import *
from models.snapshots import *

from apscheduler.scheduler import Scheduler

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
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
#if os.path.exists(CONFIG):
#    reader.read(CONFIG)
#    interval = reader.get(OPTIONS, 'cycle_connect_time')
#else:
#    interval = '12h'
def get_vm_data(username='system_user'):
    ENGINE = init_engine()
    session = create_session(ENGINE)
    session = validate_session(session)
    nodes = session.query(NodeInfo).all()
    vm = VmApi()
    vm_nodes = vm.get_all_vms()
    print vm_nodes
    for node in nodes:
        for key, value in vm_nodes.items():
            if node.host_name == value['host_name'] or \
                    node.ip_address == value['ip_address']:
                node.vm_name = value['vm_name']
                session.commit()
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
    session.close()
