
import tornado.httpserver
import tornado.web

try: import simplejson as json
except ImportError: import json

import logging
import logging.config
from models.application import *
from server.decorators import authenticated_request
from server.handlers import BaseHandler, LoginHandler
from models.base import Base
from models.packages import *
from models.node import *
from models.ssl import *
from models.scheduler import *
from db.client import *
from scheduler.jobManager import job_lister, remove_job, add_recurrent
from scheduler.timeBlocker import *
from tagging.tagManager import *
from search.search import *
from utils.common import *
from packages.pkgManager import *
from node.nodeManager import *
from transactions.transactions_manager import *
from logger.rvlogger import RvLogger
from sqlalchemy import distinct, func
from sqlalchemy.orm import sessionmaker, class_mapper

from jsonpickle import encode

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class SchedulerListerHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        result = job_lister(self.session, self.sched)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TimeBlockerListerHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        result = time_block_lister(self.session)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class SchedulerAddHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong argument passed"+
            " %s, the arguement needed is operation" % (e))
        result = job_scheduler(self.msg, self.sched, username=username)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class SchedulerRemoveHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        jobname = None
        try:
            jobname = self.get_argument('jobname')
        except Exception as e:
            self.write("Wrong arguement passed"+
            " %s, the argument needed is jobname" % (e))
        result = remove_job(self.sched, jobname, username=username)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TimeBlockerAddHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed"+
            "%s, the argument needed is operation" % (e))
        result = time_block_adder(self.session, self.msg, username=username)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TimeBlockerRemoverHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        tbid = None
        label = None
        startdate = None
        starttime = None
        try:
            tbid = self.get_argument('id')
            result = time_block_remover(self.session, tbid, username=username)
        except Exception as e:
            pass
        try:
            label = self.get_argument('label')
            start_date = self.get_argument('start_date')
            start_time = self.get_argument('start_time')
            result = time_block_remover(self.session, label, 
                    start_date, start_time)
        except Exception as e:
            pass
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TimeBlockerTogglerHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        tbid = None
        enable = ""
        try:
            tbid = self.get_argument('tbid')
            enable = self.get_argument('toggle')
            enable = return_bool(enable)
        except Exception as e:
            pass

        tb = self.session.query(TimeBlocker).\
                filter(TimeBlocker.id == tbid).first()
        if tb:
            try:
                if enable:
                    if not tb.enabled:
                        tb.enabled = True
                        self.session.commit()
                        logger.info('%s - TimeBlock %s was enabled' %\
                                (username, tbid)
                                )
                        result = {'pass' : True,
                                'message' : 'TimeBlock %s was enabled' % (tbid)
                                }
                    else:
                        logger.info('%s - TimeBlock %s was already enabled' %\
                                (username, tbid)
                                )
                        result = {'pass' : False,
                                'message' : 'TimeBlock %s was already enabled' % (tbid)
                                }
                else:
                    if tb.enabled:
                        tb.enabled = False
                        self.session.commit()
                        logger.info('%s - TimeBlock %s was disabled' %\
                                (username, tbid)
                                )
                        result = {'pass' : True,
                                'message' : 'TimeBlock %s was disabled' % (tbid)
                                }
                    else:
                        logger.info('%s - TimeBlock %s was already disabled' %\
                                (username, tbid)
                                )
                        result = {'pass' : False,
                                'message' : 'TimeBlock %s was already disabled' % (tbid)
                                }
            except Exception as e:
                self.session.rollback()
                logger.warn('%s - TimeBlock %s was not disabled or enabled' %\
                        (username, tbid)
                        )
                result = {'pass' : False,
                          'message' : 'TimeBlock %s was not disabled or enabled' % (tbid)
                          }
        else:
            logger.warn('%s - TimeBlock %s was not disabled or enabled' %\
                    (username, tbid)
                    )
            result = {'pass' : False,
                      'message' : 'TimeBlock %s was not disabled or enabled' % (tbid)
                     }
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



class SchedulerAddRecurrentJobHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        result = None
        sched = self.application.scheduler
        operation = self.get_argument('operation', None)
        severity = self.get_argument('severity', None)
        start_date = self.get_argument('start_date', None)
        year = self.get_argument('year', None)
        month = self.get_argument('month', None)
        week = self.get_argument('week', None)
        day = self.get_argument('day', None)
        day_of_week = self.get_argument('day_of_week', None)
        hour = self.get_argument('hour', None)
        minute = self.get_argument('minute', None)
        second = self.get_argument('second', None)
        jobname = self.get_argument('jobname', None)
        node_ids = self.get_arguments('nodeids')
        tag_ids = self.get_arguments('tagids')
        if operation and jobname:
            result = add_recurrent(sched, node_ids=node_ids,
                    tag_ids=tag_ids, severity=severity,
                    operation=operation, name=jobname,
                    year=year, month=month, day=day,
                    week=week, day_of_week=day_of_week,
                    hour=hour, minute=minute, second=second,
                    start_date=start_date, username=username
                    )
        else:
            result = {
                    'pass': False,
                    'message': 'invalid arguments passed'
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))
