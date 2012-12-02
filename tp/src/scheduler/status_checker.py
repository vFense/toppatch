#!/usr/bin/env python

from datetime import datetime
import logging
from db.client import *
from db.query_table import *
from db.update_table import *

from apscheduler.scheduler import Scheduler

ENGINE = init_engine()
sched = Scheduler()
sched.start()
logging.basicConfig()
@sched.interval_schedule(minutes=2)
def agent_status():
    session = create_session(ENGINE)
    session = validate_session(session)
    nodes = session.query(NodeInfo).all()
    for node in nodes:
        if node.last_agent_update:
            #timediff = node.last_agent_update - datetime.now()
            timediff = datetime.now() - node.last_agent_update
            if timediff.seconds > 480:
                node.agent_status = False
                print "AGENT IS DOWN, %d seconds since last update" % (timediff.seconds)
            else:
                node.agent_status = True
                print "AGENT IS UP, %d seconds since last update" % (timediff.seconds)
        else:
            print "Status has not been updated yet"
    session.commit()
    session.close
