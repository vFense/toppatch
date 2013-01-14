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

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class GetTransactionsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            queryCount = self.get_argument('count')
            queryOffset = self.get_argument('offset')
        except:
            queryCount = 20
            queryOffset = 0
        result = retrieve_transactions(self.session, count=queryCount, offset=queryOffset)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

        

