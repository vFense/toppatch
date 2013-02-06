#!/usr/bin/env python

from datetime import datetime
import logging, logging.config
import apscheduler
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

from networking.agentoperation import AgentOperation
from utils.common import *
from db.query_table import *
from db.client import *
from models.scheduler import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

ENGINE = init_engine()

def job_lister(session,sched):
    """
        Return a list of schedules in json 
        arguments below...
        session == sqlalchemy session)
        sched == Python Advance Schedule Object
    """
    jobs = sched.get_jobs()
    job_listing = []
    username = None
    for schedule in jobs:
        messages = schedule
        if len(schedule.args) >0:
            username = messages.args[-1]
        message = {}
        message['job_name'] = schedule.name
        message['runs'] = str(schedule.runs)
        message['job_id'] = str(schedule.id)
        message['next_run_time'] = str(schedule.next_run_time)
        message['username'] = username
        if isinstance(messages.trigger,
                apscheduler.triggers.cron.CronTrigger):
            message['schedule_type'] = 'cron'

        elif isinstance(messages.trigger,
                apscheduler.triggers.interval.IntervalTrigger):
            message['schedule_type'] = 'interval'

        elif isinstance(messages.trigger,
                apscheduler.triggers.simple.SimpleTrigger):
            message['schedule_type'] = 'once'

        if len(messages.args) == 2:
            if not isinstance(messages.args[0], list):
                jsonValid, json_msg = verify_json_is_valid(messages.args[0])
                if jsonValid:
                    if 'node_id' in json_msg:
                        node = node_exists(session, node_id=json_msg['node_id'])
                        message['ipaddress'] = node.ip_address
                        message['hostname'] = node.host_name
                        message['displayname'] = node.display_name
                        job_listing.append(message)

                    elif 'tag_id' in json_msg:
                        tag = tag_exists(session, tag_id=json_msg['tag_id'])
                        message['tagname'] = tag.tag
                        job_listing.append(message)

                else:
                    job_listing.append(message)

        elif len(messages.args) == 5:
            if isinstance(messages.args[0], str) or\
                    isinstance(messages.args[0], unicode):
                message['severity'] = messages.args[0]
                message['tag_ids'] = messages.args[1]
                message['node_ids'] = messages.args[2]
                message['operation'] = messages.args[3]
                job_listing.append(message)

        elif len(messages.args) == 4:
            if isinstance(messages.args[0], list):
                message['tag_ids'] = messages.args[0]
                message['node_ids'] = messages.args[1]
                message['operation'] = messages.args[2]
                job_listing.append(message)

        elif len(messages.args) == 1:
            job_listing.append(message)

    return job_listing


def remove_job(sched, jobname, username='system_user'):
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

def call_agent_operation(job, username):
    operation_runner = AgentOperation(job, username=username)
    operation_runner.run()


def add_once(timestamp, name, job, sched, username):
    passed = False
    try:
        sched.add_date_job(call_agent_operation,
                timestamp,args=[job, username],
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


def get_patches_and_install(severity=None, 
        tag_ids=[], node_ids=[], operation='install',
        username='system_user'):
    data = []
    job_list = []
    patches = None
    session = create_session(ENGINE)
    if len(tag_ids) >0:
        node_ids = \
                node_ids + map(lambda nodes: nodes.node_id,
                        session.query(TagsPerNode.node_id).\
                                filter(TagsPerNode.tag_id.in_(tags_ids)).all()
                                )

    if len(node_ids) >0 and severity:
        patches = session.query(Package, PackagePerNode).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                filter(PackagePerNode.installed == False).\
                filter(Package.severity == severity).\
                join(PackagePerNode).all()

    elif len(node_ids) >0 and not severity:
        patches = session.query(PackagePerNode).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                filter(PackagePerNode.installed == False).\
                join(PackagePerNode).all()

    elif len(node_ids) <1 and len(tag_ids) <1 and not severity:
        patches = session.query(PackagePerNode).\
                filter(PackagePerNode.installed == False).\
                join(PackagePerNode).all()

    elif len(node_ids) <1 and len(tag_ids) <1 and severity:
        patches = session.query(Package, PackagePerNode).\
                filter(PackagePerNode.installed == False).\
                filter(Package.severity == severity).\
                join(PackagePerNode).all()

    if patches:
        for pkg in patches:
            data.append(pkg.Package.toppatch_id)

    if len(data) >0:
        for node in node_ids:
            job = {
                    'node_id': node,
                    'operation': operation,
                    'data': data
                }
            job_list.append(job)
    
    session.close()
    if len(job_list) >0:
        call_agent_operation(job_list, username)


def recurrent_operation(node_ids=[], tag_ids=[],
    operation=None, username='system_user'):
    job = []
    if len(node_ids) >0 and operation:
        for node_id in node_ids:
            job.append({
                'node_id': node_id,
                'operation': operation
                })
        for tag_id in tag_ids:
            job.append({
                'tag_id': node_id,
                'operation': operation
                })
    call_agent_operation(job, username)

            
def add_recurrent(sched, node_ids=[], tag_ids=[],
        severity=None, operation='install',
        name=None, year=None, month=None,
        day=None, week=None, day_of_week=None,
        hour=None, minute=None, second=None,
        start_date=None, username='system_user'
        ):
    succeeded = False
    msg = 'Recurrent Scheduled added successfully'
    if re.search(r'^install|uninstall', operation) and name:
        try:
            sched.add_cron_job(get_patches_and_install,
                    year=year, month=month, day=day,
                    week=week, day_of_week=day_of_week,
                    hour=hour, minute=minute, second=second,
                    start_date=start_date,
                    args=[severity, tag_ids, node_ids, operation, username],
                    name=name, jobstore="toppatch"
                    )
            succeeded = True
        except Exception as e:
            logger.error('%s - %s' % (username, e))
            msg = 'Failed to add Recurrent Schedule'
    else:
        try:
            sched.add_cron_job(add_recurrent,
                    year=year, month=month, day=day,
                    week=week, day_of_week=day_of_week,
                    hour=hour, minute=minute, second=second,
                    start_date=start_date,
                    args=[node_ids, tag_ids, operation, username],
                    name=name, jobstore="toppatch"
                    )
            succeeded = True
        except Exception as e:
            logger.error('%s - %s' % (username, e))
            msg = 'Failed to add Recurrent Schedule'
    return({
        'pass': succeeded,
        'message': msg
        })


def job_scheduler(job, sched, name=None, username='system_user'):
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
    logger.debug('%s - %s' % (username, encoded_job_object))
    session.close()
    if 'schedule' in job_object:
        schedule = job_object['schedule']
    if 'once' in job_object['schedule']:
        return(add_once(utc_timestamp, name, encoded_job_object,
            sched, username)
            )



