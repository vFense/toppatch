
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



class TagListerByTagHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        result = tag_lister(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TagListerByNodeHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        result = tag_list_by_nodes(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TagAddHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        tag = None
        try:
            tag = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong argument passed %s, the argument needed is operation" % (e))
        result = tag_adder(self.session, tag, username=username)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TagAddPerNodeHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_add_per_node(self.session, self.msg, username=username)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TagRemovePerNodeHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_remove_per_node(self.session, self.msg,
                username=username)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TagRemoveHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        tag = None
        try:
            tag = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_remove(self.session, tag, username=username)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TagsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        session = self.application.session
        session = validate_session(session)
        tag_name = self.get_argument('tag_name', None)
        tag_id = self.get_argument('tag_id', None)
        result = None
        if tag_name:
            result = get_all_data_for_tag(session, tag_name=tag_name)
        elif tag_id:
            result = get_all_data_for_tag(session, tag_id=tag_id)
        else:
            result = {
                    'pass': False,
                    'message': 'Invalid Arguments'
                    }

        self.set_header('Content-Type', 'application/json')
        print result
        self.write(json.dumps(result, indent=4))
