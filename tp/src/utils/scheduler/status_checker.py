#!/usr/bin/env python

from datetime import datetime
import logging
from utils.db.client import *
from utils.db.query_table import *
from utils.db.update_table import *

from apscheduler.scheduler import Scheduler

ENGINE = initEngine()
sched = Scheduler()
sched.start()
logging.basicConfig()
#@sched.interval_schedule(minutes=5)
@sched.interval_schedule(minutes=2)
def agent_status():
    session = createSession(ENGINE)
    nodes = session.query(NodeInfo).all()
    for node in nodes:
        if node.last_agent_update:
            #timediff = node.last_agent_update - datetime.now()
            timediff = datetime.now() - node.last_agent_update
            minute_diff = timediff.seconds / 60
            if minute_diff > 8:
                node.agent_status = False
                print "AGENT IS DOWN, %d minutes since last update" % (minute_diff)
            else:
                node.agent_status = True
                print "AGENT IS UP, %d minutes since last update" % (minute_diff)
        else:
            print "Status has not been updated yet"
    session.commit()
    session.close
