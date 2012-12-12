#!/usr/bin/env python

from datetime import datetime
import logging, logging.config
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

from networking.agentoperation import AgentOperation
from utils.common import *
from db.query_table import *
from db.client import *
from models.scheduler import *

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

def job_lister(session,sched):
    """
        Return a list of schedules in json 
        arguments below...
        session == sqlalchemy session)
        sched == Python Advance Schedule Object
    """
    jobs = sched.get_jobs()
    job_listing = []
    for schedule in jobs:
        messages = schedule.args
        for message in messages:
            if type(message) == str:
                jsonValid, message = verify_json_is_valid(message)
                if jsonValid:
                    if 'node_id' in message:
                        node = node_exists(session, node_id=message['node_id'])
                        message['ipaddress'] = node.ip_address
                        message['hostname'] = node.host_name
                        message['displayname'] = node.display_name
                        job_listing.append(message)
                    elif 'tag_id' in message:
                        tag = tag_exists(session, tag_id=message['tag_id'])
                        message['tagname'] = tag.tag
                        job_listing.append(message)
    return job_listing

def remove_job(sched, jobname):
    """
        remove the scheduled job in RV
        arguments below..
        sched == Python Advance Schedule Object
        jobname == the name of the scheduled job
    """
    jobs = sched.get_jobs()
    count = 0
    for schedule in jobs:
        if jobname in schedule.name:
            try:
                sched.unschedule_job(schedule)
                count = count + 1
                return({"schedule_name" : jobname,
                        "pass" : True,
                         "message" : "Job with name %s was removed"\
                                     % (jobname)
                        })
            except:
                count = count + 1
                return({"schedule_name" : jobname,
                        "pass" : False,
                         "message" : "Job with name %s could not be removed"\
                                     % (jobname)
                        })
    if count == 0:
        return({"schedule_name" : jobname,
                "pass" : False,
                "message" : "Job with name %s does not exist" % (jobname)
               })

def call_agent_operation(job):
    operation_runner = AgentOperation(job)
    operation_runner.run()

def add_once(timestamp, name, job, sched):
    passed = False
    try:
        sched.add_date_job(call_agent_operation,
                timestamp,args=[job],
                name=name, jobstore="toppatch"
                )
        passed = True
    except Exception as e:
        if e.message:
            passed = False
    if passed:
        return({
                'pass' : True,
                'message' : 'Schedule %s has been added to this time frame %s '\
                        % (name, timestamp)
               })
    else:
        return({'pass': False,
                'message': e.message
               })

def add_recurrent(timestamp, name, job, sched):
    sched.add_date_job(call_agent_operation,
                timestamp,args=[job],
                name=name, jobstore="toppatch"
                )

def job_scheduler(job, sched, name=None):
    """
        job_scheduler handles the adding of scheduled jobs
        arguments below...
        job == this contains the operation and related information that the 
        schedule will perform. This also contains the start date and time.
        name == The name of the scheduled job
    """
    ENGINE = init_engine()
    session = create_session(ENGINE)
    log = logging.basicConfig()
    converted_timestamp = None
    schedule = None
    json_valid, job_object = verify_json_is_valid(job[0])
    if 'Default' in  job_object['label']:
        name = job_object['operation'] + " " + job_object['time']
        job_object['label'] = job_object['operation'] + " " + job_object['time']
    else:
        name = job_object['label']
    if 'time' in job_object:
        utc_timestamp = date_time_parser(job_object['time'])
        time_block_exists, time_block, json_out = \
                time_block_exists_today(session,
                    start_date=utc_timestamp.date(),
                    start_time=utc_timestamp.time())
        if time_block_exists:
            return json_out
    encoded_job_object = dumps(job_object)
    logger.debug(encoded_job_object)
    if 'schedule' in job_object:
        schedule = job_object['schedule']
    if 'once' in job_object['schedule']:
        return(add_once(utc_timestamp, name, encoded_job_object, sched))



