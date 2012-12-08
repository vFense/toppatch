#!/usr/bin/env python

from datetime import datetime
import logging
import re
from subprocess import Popen, PIPE, STDOUT
from db.client import *
from db.query_table import *
from db.update_table import *

from apscheduler.scheduler import Scheduler

ENGINE = init_engine()
sched = Scheduler()
sched.start()
logging.basicConfig()
@sched.interval_schedule(minutes=3)
def agent_status():
    ping_cmd = '/bin/ping -c1 -W1 '
    session = create_session(ENGINE)
    session = validate_session(session)
    nodes = session.query(NodeInfo).all()
    for node in nodes:
        if node.last_agent_update and node.last_node_update:
            #timediff = node.last_agent_update - datetime.now()
            timediffagent = datetime.now() - node.last_agent_update
            timediffnode = datetime.now() - node.last_node_update
            if timediffagent.seconds > 480:
                node.agent_status = False
                print "AGENT IS DOWN, %d seconds since last update" %\
                        (timediffagent.seconds)
            else:
                node.agent_status = True
                print "AGENT IS UP, %d seconds since last update" %\
                        (timediffagent.seconds)
            if timediffnode.seconds > 480:
                ping_cmd = ping_cmd + node.ip_address
                output = Popen([ping_cmd], shell=True, stdout=PIPE,
                        stderr=STDOUT)
                stdout = output.stdout.read()
                percent = re.search(r'([0-9]+)\% packet loss',stdout)
                if percent:
                    if percent.group(1) <= '100' and percent.group(1) > '0':
                        node.node_status = False
                        print "NODE IS UP, %d seconds since last update" %\
                            (timediffnode.seconds)
                else:
                    node.node_status = True
                    print "NODE IS DOWN, %d seconds since last update" %\
                            (timediffnode.seconds)
            else:
                node.node_status = True
                print "NODE IS UP, %d seconds since last update" %\
                        (timediffnode.seconds)
        else:
            print "Status has not been updated yet"
    session.commit()
    session.close
