#!/usr/bin/env python

from datetime import datetime
import logging
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
