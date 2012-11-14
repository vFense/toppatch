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
from utils.db.update_table import addTimeBlock, removeTimeBlock
from models.scheduler import *

def timeBlockLister(session):
    blocks = session.query(TimeBlocker).all()
    windows = []
    if blocks:
        for block in blocks:
            days_enabled, days_not_enabled = returnDays(block.days)
            if block.start_date:
                start_date = '%s/%s/%s' % \
                        (
                        str(block.start_date.month).rjust(2,'0'),
                        str(block.start_date.day).rjust(2,'0'),
                        str(block.start_date.year)
                        )
            else:
                start_date = block.start_date
            if block.end_date:
                end_date = '%s/%s/%s' % \
                        (
                        str(block.end_date.month).rjust(2,'0'),
                        str(block.end_date.day).rjust(2,'0'),
                        str(block.end_date.year)
                        )
            else:
                end_date = block.end_date
            if block.start_time:
                start_time = '%s:%s' % \
                        (
                        str(block.start_time.hour).rjust(2,'0'),
                        str(block.start_time.minute).ljust(2,'0')
                        )
            else:
                start_time = block.start_time
            if block.end_time:
                end_time = '%s:%s' % \
                        (
                        str(block.end_time.hour).rjust(2,'0'),
                        str(block.end_time.minute).ljust(2,'0')
                        )
            else:
                end_time = block.end_time


            msg = {
                   'name' : block.name,
                   'enabled' : block.enabled,
                   'start_date' : start_date,
                   'end_date' : end_date,
                   'start_time' : start_time,
                   'end_time' : end_time,
                   'days_enabled' : days_enabled,
                   'days_disabled' : days_not_enabled
                   }
            encoded_msg = encode(msg)
            windows.append(encoded_msg)
    else:
        windows = '{"message" : "There arent any windows"}'
    return windows

def timeBlockRemover(session,msg):
    """The message needs to be in a valid json format.
    either you must pass the time block id or 
    the time block label, start_date, and start_time
    {"id" : "1"} 
    or 
    {"label" : "test block",
    "start_date" : "12/15/2012",
    "start_time" : "09:00 AM"
    }
    """
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if 'id' in json_msg:
            removed = removeTimeBlock(session, id=json_msg['id'])
        elif 'label' and 'start_date' and 'start_time' in json_msg:
            label = json_msg['label']
            start_date = dateTimeParser(json_msg['start_date'])
            start_time = dateTimeParser(json_msg['start_time'])
            removed = removeTimeBlock(session, label=label, 
                    start_date=start_date, start_time=start_time
                    )
        if removed:
            message = '{pass : %s, message %s}' \
                    % (removed[0], removed[1])
        return removed

def timeBlockAdder(session, msg):
    """The message needs to be in a valid json format.
       end_date is optional. Our date format is in binary format...
       So if you have a schedule that is Mon through Fri, it will look
       like this... "0111110" Week begins with Sunday.

        {"label" : "9am to 5pm, Mon to Fri",
        "enabled" : "True", (DEFAULT IS True)
        "start_date" : "11/14/2012",
        "end_date" : "11/14/2013", (OPTIONAL)
        "start_time" : "09:00 AM",
        "end_time" : "05:00 PM",
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
        else:
           json_msg['end_date'] = dateParser(json_msg['end_date']) 
        if 'start_date' in json_msg:
           json_msg['start_date'] = dateParser(json_msg['start_date']) 
        if 'start_time' in json_msg:
           json_msg['start_time'] = dateTimeParser(json_msg['start_time']) 
        if 'end_time' in json_msg:
           json_msg['end_time'] = dateTimeParser(json_msg['end_time']) 
        block_added, message, block = addTimeBlock(session, json_msg['label'],
                json_msg['enabled'], json_msg['start_date'],
                json_msg['end_date'], json_msg['start_time'],
                json_msg['end_time'], json_msg['days']
                )

        return '{message : %s,label : %s}'\
                    % (message, json_msg["label"])

