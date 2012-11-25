#!/usr/bin/env python

from datetime import datetime
import logging
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

from networking.agentoperation import AgentOperation
from utils.common import *
from db.query_table import *
from db.client import *
from models.scheduler import *

def jobLister(session,sched):
    jobs = sched.get_jobs()
    job_listing = []
    for schedule in jobs:
        messages = schedule.args
        for message in messages:
            if type(message) == str:
                jsonValid, message = verifyJsonIsValid(message)
                if jsonValid:
                    node_obj, node = nodeExists(session, node_id=message['node_id'])
                    message['node_id'] = node.ip_address
                    job_listing.append(message)
    return job_listing

def removeJob(sched, jobname):
    jobs = sched.get_jobs()
    count = 0
    for schedule in jobs:
        if jobname in schedule.name:
            try:
                sched.unschedule_job(schedule)
                count = count + 1
                return({"schedule_name" : jobname,
                        "job_deleted" : True,
                         "message" : "Job with name %s was removed"\
                                     % (jobname)
                        })
            except:
                count = count + 1
                return({"schedule_name" : jobname,
                        "job_deleted" : False,
                         "message" : "Job with name %s could not be removed"\
                                     % (jobname)
                        })
    if count == 0:
        return({"schedule_name" : jobname,
                "job_deleted" : False,
                "message" : "Job with name %s does not exist" % (jobname)
               })

def callAgentOperation(job):
    operation_runner = AgentOperation(job)
    operation_runner.run()

def addOnce(timestamp, name, job, sched):
    sched.add_date_job(callAgentOperation,
                timestamp,args=[job],
                name=name, jobstore="toppatch"
                )

def addRecurrent(timestamp, name, job, sched):
    sched.add_date_job(callAgentOperation,
                timestamp,args=[job],
                name=name, jobstore="toppatch"
                )

def JobScheduler(job, sched, name=None):
        ENGINE = initEngine()
        session = createSession(ENGINE)
        log = logging.basicConfig()
        converted_timestamp = None
        schedule = None
        json_valid, job_object = verifyJsonIsValid(job[0])
        if 'Default' in  job_object['label']:
            name = job_object['operation'] + " " + job_object['time']
            job_object['label'] = job_object['operation'] + " " + job_object['time']
        else:
            name = job_object['label']
        if 'time' in job_object:
            utc_timestamp = dateTimeParser(job_object['time'])
            time_block_exists, time_block, json_out = \
                    timeBlockExistsToday(session,
                        start_date=utc_timestamp.date(),
                        start_time=utc_timestamp.time())
            print time_block_exists, time_block, json_out
            if time_block_exists:
                return json_out
        encoded_job_object = dumps(job_object)
        print encoded_job_object
        if 'schedule' in job_object:
            schedule = job_object['schedule']
        if 'once' in job_object['schedule']:
            addOnce(utc_timestamp, name, encoded_job_object, sched)
            return({
                    "pass" : True,
                    "message" : "Schedule %s has been added to this time frame %s " % (name, utc_timestamp)
                   })



