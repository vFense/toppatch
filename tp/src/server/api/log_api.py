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

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class LoggingModifyerHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        host = self.get_argument('host', None)
        port = self.get_argument('port', None)
        proto = self.get_argument('proto', 'UDP')
        level = self.get_argument('level', 'INFO')
        proto = proto.upper()
        level = level.upper()
        if host and port and proto and level:
            rvlogger = RvLogger()
            connected = rvlogger.connect_to_loghost(host, port, proto)
            if connected:
                rvlogger.create_config(loglevel=level, loghost=host,
                        logport=port, logproto=proto)
                results = rvlogger.results
            else:
                results = {
                        'pass': False,
                        'message': 'Cant connect to %s on %s using proto %s' %\
                                (host, port, proto)
                        }
        elif level and not host and not port:
            rvlogger = RvLogger()
            rvlogger.create_config(loglevel=level)
            results = rvlogger.results
        else:
            results = {
                    'pass': False,
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
