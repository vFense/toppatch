#!/usr/bin/env python

from datetime import datetime
import logging
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

from utils.agentoperation import AgentOperation
from utils.common import *

def jobLister(session,vsched):
    jobs = sched.get_jobs()
    job_listing = []
    for schedule in jobs:
        messages = schedule.args[0]
        for message in messages:
            jsonValid, message = verifyJsonIsValid(message)
            message['time'] = returnDatetime(message['time'])
            node_obj, node = nodeExists(session, node_id=message['node_id'])
            message['node_id'] = node.ip_address
            job_listing.append(message)
    return job_listing

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
        log = logging.basicConfig()
        converted_timestamp = None
        schedule = None
        json_valid, job_object = verifyJsonIsValid(job[0])
        if not name:
            name = job_object['operation']
        if 'time' in job_object:
            converted_timestamp = returnDatetime(job_object['time'])
        if 'schedule' in job_object:
            schedule = job_object['schedule']
        if 'once' in job_object['schedule']:
            addOnce(converted_timestamp, name, job, sched)


