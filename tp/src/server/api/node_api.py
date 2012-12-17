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

class ModifyDisplayNameHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        nodeid = None
        displayname = None
        try:
            nodeid = self.get_argument('nodeid')
            displayname = self.get_argument('displayname')
        except Exception as e:
            pass
        if nodeid and displayname:
            node = self.session.query(NodeInfo).filter(NodeInfo.id == nodeid).first()
            if node:
                try:
                    if re.search(r'none', displayname, re.IGNORECASE):
                        displayname = return_bool(displayname)
                    node.display_name = displayname
                    self.session.commit()
                    logger.info('%s - Display name was changed to %s' %\
                            (username, displayname)
                            )
                    result = {"pass" : True,
                              "message" : "Display name change to %s" %\
                                            (displayname)
                            }
                except Exception as e:
                    self.session.rollback()
                    logger.error('%s - Display name was not changed to %s' %\
                            (username, displayname)
                            )
                    result = {"pass" : False,
                              "message" : "Display name was not changed to %s"%\
                                            (displayname)
                            }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class ModifyHostNameHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        nodeid = None
        hostname = None
        try:
            nodeid = self.get_argument('nodeid')
            hostname = self.get_argument('hostname')
        except Exception as e:
            pass
        if nodeid and hostname:
            node = self.session.query(NodeInfo).filter(NodeInfo.id == nodeid).first()
            if node:
                try:
                    if re.search(r'none', hostname, re.IGNORECASE):
                        hostname = return_bool(hostname)
                    node.host_name = hostname
                    self.session.commit()
                    logger.info('%s - Host name was changed to %s' %\
                            (username, hostname)
                            )
                    result = {"pass" : True,
                              "message" : "Host name change to %s" %\
                                            (hostname)
                            }
                except Exception as e:
                    self.session.rollback()
                    logger.error('%s - Host name was not changed to %s' %\
                            (username, hostname)
                            )
                    result = {"pass" : False,
                              "message" : "Host name was not changed to %s"%\
                                            (hostname)
                            }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



