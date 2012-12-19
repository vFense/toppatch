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


class SearchPatchHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        output = 'json'
        try:
            query = self.get_argument('query')
            column = self.get_argument('searchby')
            count = self.get_argument('count')
            offset = self.get_argument('offset')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is toppatch_id" % (e))
        try:
            output = self.get_argument('output')
        except Exception as e:
            pass
        result = basic_package_search(self.session, query, column, count=count, offset=offset, output=output)
        if 'json' in output:
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result, indent=4))
        elif 'csv' in output:
            self.set_header('Content-Type', 'application/csv')
            self.write(result)


class PatchesHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        patch_oper = re.compile(r'installed|available|pending|failed')
        patch_sev = re.compile(r'Critical|Optional|Recommended')
        tpid = self.get_argument('id', None)
        queryCount = self.get_argument('count', 10)
        queryOffset = self.get_argument('offset', 0)
        pstatus = self.get_argument('type', None)
        patches = PatchRetriever(self.session,
            qcount=queryCount, qoffset=queryOffset)
        if tpid:
            results = patches.get_by_toppatch_id(tpid)
        elif pstatus:
            if patch_oper.search(pstatus):
                results = patches.get_by_type(pstatus)
            elif patch_sev:
                results = patches.get_by_severity(pstatus)
            else:
                results = {"pass": False, "message":
                        "Invalid Status or Severity"
                        }
        else:
            results = patches.get_pkg_default()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class SeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        session = self.application.session
        session = validate_session(session)
        for sev in session.query(Package.severity).distinct().all():
            count = session.query(Package, PackagePerNode).\
                    filter(Package.severity == sev.severity).\
                    filter(PackagePerNode.installed == False).\
                    group_by(PackagePerNode.toppatch_id).join(PackagePerNode).count()
            result_json = { 'label' : str(sev.severity), 'value' : count }
            result.append(result_json)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class GetTagsPerTpIdHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        tpid = self.get_argument('tpid', None)
        if tpid:
            result = list_tags_per_tpid(self.session, tpid)
        else:
            result({
                'pass': False,
                'message': 'please pass tpid'
                })
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



class GetDependenciesHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            pkg_id = self.get_argument('toppatch_id')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is toppatch_id" % (e))
        result = retrieve_dependencies(self.session, pkg_id)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

