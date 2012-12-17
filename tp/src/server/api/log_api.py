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
from server.handlers import SendToSocket
from db.client import *
from scheduler.jobManager import job_lister, remove_job
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

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')


class LoggingModifyerHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        level = 'INFO'
        host = None
        port = None
        proto = None
        passed = None
        try:
            host = self.get_argument('host')
            port = self.get_argument('port')
            proto = self.get_argument('proto')
            proto = proto.upper()
            level = self.get_argument('level')
            level = level.upper()
            rvlogger = RvLogger()
            connected = rvlogger.connect_to_loghost(host, port, proto)
            if connected:
                rvlogger.create_config(loglevel=level, loghost=host,
                        logport=port, logproto=proto)
                results = rvlogger.results
                passed = True
            else:
                passed = False
                results = {
                        'pass': False,
                        'message': 'Cant connect to %s on %s using proto %s' %\
                                (host, port, proto)
                                }
        except Exception as e:
            try:
                level = self.get_argument('level')
                rvlogger = RvLogger()
                rvlogger.create(loglevel=level)
                results = rvlogger.results
            except Exception as f:
                passed = False
                results = {
                    'pass': passed,
                    'message': 'incorrect parameters passed'
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class LoggingListerHandler(BaseHandler):
    @authenticated_request
    def get(self):
        rvlogger = RvLogger()
        rvlogger.get_logging_config()
        results = rvlogger.results
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
