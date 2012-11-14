#!/usr/bin/env python

from datetime import datetime
import logging
import re
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
from jsonpickle import encode

from utils.agentoperation import AgentOperation
from utils.common import *
from utils.db.query_table import nodeExists
from models.scheduler import *

def timeBlockLister(session):
    blocks = session.query(TimeBlocker).all
    windows = []
    for block in blocks:
        days_enabled, days_not_enabled = returnDays(block.days)
        msg = {
               'name' : block.name,
               'enabled' : block.enabled,
               'start_date' : block.start_date,
               'end_date' : block.end_date,
               'start_time' : block.start_time,
               'duration' : block.duration,
               'days_enabled' : block.days_enabled,
               'days_disabled' : block.days_not_enabled
               }
        encoded_msg = encode(msg)
        windows.append(encoded_message)
    return windows

def timeBlockAdder(session, msg):
    """The message needs to be in a valid json format.
       end_date is optional. Our date format is in binary format...
       So if you have a schedule that is Mon through Fri, it will look
       like this... "0111110" Week begins with Sunday.

        {"name" : "9am to 5pm, Mon to Fri",
        "enabled" : "True", (DEFAULT IS True)
        "start_date" : "11/14/2012",
        "end_date" : "11/14/2013", (OPTIONAL)
        "start_time" : "09:00 AM",
        "duration" : "8",
        "days" : "0111110"
        }
    """
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if not 'enabled' in json_msg:
            json_msg['enabled'] = True
        else:
            if re.search(r'true', json_msg['enabled'], re.IGNORECASE):
                json_msg['enabled'] = True
            elif re.search(r'false', json_msg['enabled'], re.IGNORECASE):
                json_msg['enabled'] = False
        if not 'end_date' in json_msg:
            json_msg['end_date'] = None
         block_added = addBlock(session, json_msg['name'],
                json_msg['enabled'], json_msg['start_date'],
                json_msg['end_date'], json_msg['start_time'],
                json_msg['duration'], json_msg['days']
                )

