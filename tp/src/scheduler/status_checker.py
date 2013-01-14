#!/usr/bin/env python

from datetime import datetime
import logging, logging.config
import re
from subprocess import Popen, PIPE, STDOUT
from db.client import *
from db.query_table import *
from db.update_table import *

from apscheduler.scheduler import Scheduler

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

ENGINE = init_engine()
sched = Scheduler()
sched.start()
@sched.interval_schedule(minutes=3)
def agent_status():
    ping_cmd = '/bin/ping -c1 -W1 '
    session = create_session(ENGINE)
    session = validate_session(session)
    nodes = session.query(NodeInfo).all()
    username = 'system_user'
    for node in nodes:
        if node.last_agent_update and node.last_node_update:
            timediffagent = datetime.now() - node.last_agent_update
            timediffnode = datetime.now() - node.last_node_update
            if timediffagent.seconds > 480:
                node.agent_status = False
                logger.info('%s - AGENT %s is DOWN, %d seconds since last update' %\
                        (username, node.ip_address, timediffagent.seconds)
                        )
            else:
                node.agent_status = True
                logger.info('%s - AGENT %s is UP, %d seconds since last update' %\
                        (username, node.ip_address, timediffagent.seconds)
                        )
            if timediffnode.seconds > 480:
                ping_cmd = ping_cmd + node.ip_address
                output = Popen([ping_cmd], shell=True, stdout=PIPE,
                        stderr=STDOUT)
                stdout = output.stdout.read()
                percent = re.search(r'([0-9]+)\% packet loss',stdout)
                if percent:
                    if int(percent.group(1)) <= 99:
                        node.host_status = True
                        logger.info('%s - NODE %s is UP, %d seconds since last update'%\
                                (username, node.ip_address, timediffagent.seconds)
                                )
                    elif int(percent.group(1)) == 100:
                        node.host_status = False
                        logger.info('%s - NODE %s is DOWN, %d seconds since last update'%\
                                (username, node.ip_address, timediffnode.seconds)
                                )
                else:
                    node.host_status = False
                    logger.info('%s - NODE %s is DOWN, %d seconds since last update'%\
                           (username, node.ip_address, timediffnode.seconds)
                           )
            else:
                node.host_status = True
                logger.info('%s - NODE %s is UP, %d seconds since last update'%\
                       (username, node.ip_address, timediffnode.seconds)
                       )
        else:
            logger.info('%s - Status for %s has not been updated yet' %\
                    (username, node.ip_address)
                    )
    session.commit()
    session.close
