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


class NetworkHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = []
        self.session = self.application.session
        self.session = validate_session(self.session)
        for u in self.session.query(NetworkStats).all():
            resultjson.append({"key" : "installed",
                "data" : u.patches_installed})
            resultjson.append({"key" : "available",
                "data" : u.patches_available})
            resultjson.append({"key" : "pending",
                "data" : u.patches_pending})
            resultjson.append({"key" : "failed",
                "data" : u.patches_failed})
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))


class SummaryHandler(BaseHandler):
    @authenticated_request
    def get(self):
        osResult = []
        session = self.application.session
        session = validate_session(session)
        for u in session.query(SystemInfo.os_code).distinct().all():
            osTypeResult = []
            for v in session.query(SystemInfo.os_string).\
                    filter(SystemInfo.os_code == u.os_code).\
                    distinct().all():
                nodeResult = []
                for w in session.query(NodeInfo, SystemInfo, NodeStats).\
                        join(SystemInfo).join(NodeStats).\
                        filter(SystemInfo.os_string == v.os_string).\
                        distinct().all():
                    nodeResult.append({"name" : w[0].ip_address,
                                       "children" : [
                                           {"name" : "Patches Installed",
                                               "size" : w[2].patches_installed},
                                           {"name" : "Patches Available",
                                               "size" : w[2].patches_available},
                                           {"name" : "Patches Pending",
                                               "size" : w[2].patches_pending},
                                           {"name" : "Patches Failed",
                                               "size" : w[2].patches_failed}
                                           ]
                                       }
                                       )
                osTypeResult.append({"name" : v.os_string,
                    "children" : nodeResult})
            osResult.append({"name" : u.os_code,
                "children" : osTypeResult})
        root = {"name" : "192.168.1.0",
                "children" : osResult }
        session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(root))


class GraphHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = []
        osType = []
        self.session = self.application.session
        self.session = validate_session(self.session)
        for u in self.session.query(SystemInfo.os_string,
                func.count(SystemInfo.os_string)).\
                        group_by(SystemInfo.os_string).all():
            nodeResult = []
            for v in self.session.query(NodeInfo, SystemInfo, NodeStats).\
                    filter(SystemInfo.os_string == u[0]).join(SystemInfo).\
                    join(NodeStats).all():
                nodeResult.append({"name" : v[0].ip_address,
                                   "os" : v[1].os_string,
                                   "children" : [{"name" : "Patches Installed",
                                       "size" : v[2].patches_installed,
                                       "graphData" : {"label" : v[0].ip_address,
                                           "value" : v[2].patches_installed
                                           }
                                    },
                                {"name" : "Patches Available",
                                    "size" : v[2].patches_available,
                                    "graphData" : {"label" : v[0].ip_address,
                                        "value" : v[2].patches_available
                                    }
                                },
                                {"name" : "Patches Pending",
                                    "size" : v[2].patches_pending,
                                    "graphData" : {"label" : v[0].ip_address,
                                        "value" : v[2].patches_pending
                                        }
                                },
                                {"name" : "Patches Failed",
                                    "size" : v[2].patches_failed,
                                    "graphData" : {"label" : v[0].ip_address,
                                        "value" : v[2].patches_failed
                                        }
                                    }
                                ]
                                   }
                                   )
            osType.append({"label" : u[0], "value" : u[1], "data" : nodeResult})
        resultjson = osType
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))


class OsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = []
        installed = 0
        available = 0
        pending = 0
        failed = 0
        type = self.get_argument('type')
        self.session = self.application.session
        self.session = validate_session(self.session)
        for u in self.session.query(NodeInfo, SystemInfo, NodeStats).\
                filter(SystemInfo.os_string == type).join(SystemInfo).\
                join(NodeStats).all():
            installed += u[2].patches_installed
            available += u[2].patches_available
            pending += u[2].patches_pending
            failed += u[2].patches_failed
        if installed or available or pending or failed:
            resultjson.append({"label" : "Installed",
                "value" : installed})
            resultjson.append({"label" : "Available",
                "value" : available})
            resultjson.append({"label" : "Pending",
                "value" : pending})
            resultjson.append({"label" : "Failed",
                "value" : failed})
            self.session.close()
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson, indent=4))
        else:
            self.session.close()
            resultjson = {'error' : 'no data to display'}
            self.write(json.dumps(resultjson, indent=4))


