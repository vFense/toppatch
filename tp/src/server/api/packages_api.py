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


class SearchPatchHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        output = 'json'
        query = self.get_argument('query', None)
        column = self.get_argument('searchby', None)
        count = self.get_argument('count', 10)
        offset = self.get_argument('offset', 0)
        by_date = self.get_argument('date', None)
        output = self.get_argument('output', 'json')
        installed = self.get_argument('installed', None)
        nodeid = self.get_argument('nodeid', None)
        tagid = self.get_argument('tagid', None)
        if installed and type(installed) != bool:
            installed = return_bool(installed)
        if by_date:
            by_date = date_parser(by_date, by_year=True)
        result = basic_package_search(self.session, query, column,
                count=count, offset=offset, by_date=by_date,
                installed=installed, nodeid=nodeid,
                tagid=tagid, output=output)
        self.session.close()
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
        pstatus = self.get_argument('status', None)
        severity = self.get_argument('severity', None)
        nodeid = self.get_argument('nodeid', None)
        patches = PatchRetriever(self.session,
            qcount=queryCount, qoffset=queryOffset)
        if tpid:
            results = patches.get_by_toppatch_id(tpid)
        elif pstatus:
            if patch_oper.search(pstatus):
                if nodeid:
                    results = patches.get_by_type(pstatus, nodeid)
                else:
                    results = patches.get_by_type(pstatus)
            else:
                results = {
                        'pass': False,
                        'message': 'Invalid Status'
                        }
        elif severity:
            if patch_sev.search(severity):
                if nodeid:
                    results = patches.get_by_severity(severity, nodeid)
                else:
                    results = patches.get_by_severity(severity)
            else:
                results = {
                        'pass': False,
                        'message': 'Invalid Severity'
                        }
        else:
            results = patches.get_pkg_default()
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class SeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        session = self.application.session
        session = validate_session(session)
        optional = None
        recommended = None
        critical = None
        tp_ids = map(lambda x: x[0],
                session.query(Package.toppatch_id).\
                    filter(PackagePerNode.installed == False).\
                    group_by(Package.toppatch_id).\
                    join(PackagePerNode).all())
        severities = \
                session.query(func.count(Package.severity),
                    Package.severity).group_by(Package.severity).\
                    filter(PackagePerNode.installed == False).\
                    join(PackagePerNode).all()
                    #filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
        optional = len(session.query(PackagePerNode).\
            filter(Package.severity == 'Optional').\
            filter(PackagePerNode.installed == False).\
            group_by(PackagePerNode.toppatch_id).\
            join(Package).all())
        recommended = len(session.query(PackagePerNode).\
            filter(Package.severity == 'Recommended').\
            filter(PackagePerNode.installed == False).\
            group_by(PackagePerNode.toppatch_id).\
            join(Package).all())
        critical = len(session.query(PackagePerNode).\
            filter(Package.severity == 'Critical').\
            filter(PackagePerNode.installed == False).\
            group_by(PackagePerNode.toppatch_id).\
            join(Package).all())
        severities = [ (optional, 'Optional'), (recommended, 'Recommended'),
                (critical, 'Critical') ]
        for sev in severities:
            result.append(
                    { 
                        'label' : sev[1],
                        'value' : sev[0]
                    })
        session.close()
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
        self.session.close()
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
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

