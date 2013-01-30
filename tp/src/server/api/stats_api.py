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


class GetTagStatsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        tag_id = self.get_argument('tagid', None)
        tag_name = self.get_argument('tagname', None)
        result = get_tag_stats(self.session, tagid=tag_id, tagname=tag_name)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class GetNodeStatsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        nodeid = self.get_argument('nodeid')
        nodename = self.get_argument('nodename')
        result = get_node_stats(self.session, tagid=tag_id, tagname=tag_name)
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class BasePackageSeverityOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self):
        session = self.application.session
        session = validate_session(session)
        nodeid = self.get_argument('nodeid', None)
        tagid = self.get_argument('tagid', None)
        installed = self.get_argument('installed', True)
        self.data = []
        self.total = 0
        self.optional = 0
        self.recommended = 0
        self.critical = 0
        self.total_critical = None
        self.total_recommended = None
        self.total_optional = None
        date_installed = None
        date_available = None
        from datetime import datetime
        if type(installed) != bool:
            installed = return_bool(installed)

        if not nodeid:
            if installed:
                tp_ids = map(lambda x: x[0],
                        session.query(PackagePerNode.toppatch_id)\
                                .group_by(PackagePerNode.toppatch_id).\
                                filter(PackagePerNode.installed == True).all())

                self.total_critical = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == True).\
                    filter(Package.severity == 'Critical').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
                self.total_optional = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == True).\
                    filter(Package.severity == 'Optional').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
                self.total_recommended = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == True).\
                    filter(Package.severity == 'Recommended').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())


                date_installed = map(lambda x: x[0], 
                        session.query(func.date(PackagePerNode.date_installed)).\
                            filter(PackagePerNode.installed == True).\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            group_by(func.date(PackagePerNode.date_installed)).all()
                            )

                for line in date_installed:
                    if not line:
                        continue
                    critical = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Critical').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    optional = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Optional').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    recommended = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Recommended').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    self._parse_data(optional, recommended, critical, line)


            else:
                tp_ids = \
                        map(lambda x: x[0], session.query(PackagePerNode.toppatch_id).\
                        group_by(PackagePerNode.toppatch_id).\
                        filter(PackagePerNode.installed == False).all())

                dates_avail = \
                        map(lambda x: x[0], session.query(func.date(Package.date_pub)).\
                        group_by(Package.date_pub).
                        filter(Package.toppatch_id.in_(tp_ids)).all())

                self.total_critical = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == False).\
                    filter(Package.severity == 'Critical').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
                self.total_optional = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == False).\
                    filter(Package.severity == 'Optional').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
                self.total_recommended = len(session.query(PackagePerNode).\
                    filter(PackagePerNode.installed == False).\
                    filter(Package.severity == 'Recommended').\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
                #self.total_critical, self.total_optional, self.total_recommended = \
                #        map(lambda x: x[0],
                #            session.query(func.count(Package.severity)).\
                #                    group_by(Package.severity).\
                #                    filter(PackagePerNode.installed == False).\
                #                    filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                #                    join(PackagePerNode).all()
                #            )
                print datetime.now(), 'getting packages'
                for line in dates_avail:
                    if not line:
                        continue
                    #pkg_query = session.query(func.count(Package.severity),
                    #        Package.severity).group_by(Package.severity).\
                    #            filter(func.date(Package.date_pub) == line).\
                    #            filter(PackagePerNode.installed == False).\
                    #            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                    #            join(PackagePerNode).all()
                    critical = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Critical').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    optional = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Optional').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    recommended = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Recommended').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    self._parse_data(optional, recommended, critical, line)
                print datetime.now(), 'done getting packages'

        elif tagid or nodeid:
            if tagid:
                node_ids = map(lambda x: x[0], s.query(TagsPerNode.node_id).\
                        filter(TagsPerNode.tag_id == 1).all())
            elif nodeid:
                node_ids = [nodeid]
            tp_ids = map(lambda x: x[0],
                    session.query(PackagePerNode.toppatch_id)\
                        .group_by(PackagePerNode.toppatch_id).\
                        filter(PackagePerNode.installed == installed).\
                        filter(PackagePerNode.node_id.in_(node_ids)).all())

            self.total_critical = len(session.query(PackagePerNode).\
                    filter(Package.severity == 'Critical').\
                    filter(PackagePerNode.installed == installed).\
                    filter(PackagePerNode.node_id.in_(node_ids)).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
            self.total_recommeneded = len(session.query(PackagePerNode).\
                    filter(Package.severity == 'Recommended').\
                    filter(PackagePerNode.installed == installed).\
                    filter(PackagePerNode.node_id.in_(node_ids)).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())
            self.total_optional = len(session.query(PackagePerNode).\
                    filter(Package.severity == 'Optional').\
                    filter(PackagePerNode.installed == installed).\
                    filter(PackagePerNode.node_id.in_(node_ids)).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(Package).all())

            if installed:
                date_installed = map(lambda x: x[0],
                        session.query(func.date(PackagePerNode.date_installed)).\
                            filter(PackagePerNode.installed == installed).\
                            filter(PackagePerNode.node_id.in_(node_ids)).\
                            group_by(func.date(PackagePerNode.date_installed)).all()
                            )

                for line in date_installed:
                    critical = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Critical').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    optional = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Optional').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    recommended = len(session.query(PackagePerNode).\
                            filter(func.date(PackagePerNode.date_installed) == line).\
                            filter(PackagePerNode.installed == True).\
                            filter(Package.severity == 'Recommended').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    self._parse_data(optional, recommended, critical, line)


            else:
                date_available = map(lambda x: x[0], 
                        session.query(func.date(Package.date_pub)).\
                            filter(PackagePerNode.installed == False).\
                            filter(PackagePerNode.node_id.in_(node_ids)).\
                            group_by(func.date(PackagePerNode.date_installed)).all()
                            )

                for line in date_available:
                    critical = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Critical').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    optional = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Optional').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    recommended = len(session.query(PackagePerNode).\
                            filter(func.date(Package.date_pub) == line).\
                            filter(PackagePerNode.installed == False).\
                            filter(Package.severity == 'Recommended').\
                            filter(PackagePerNode.toppatch_id.in_(tp_ids)).\
                            join(Package).all())
                    self._parse_data(optional, recommended, critical, line)


        results = {
                'total': self.total,
                'optional': self.total_optional,
                'recommended': self.total_recommended,
                'critical': self.total_critical,
                'dates': self.data
                }
        session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


    def _parse_data(self, optional, recommended, critical, date1):
#        print optional, recommended, critical
        row_data = {}
        #row_data['total'] = sum(map(lambda x: x[0], row_pkg))
        row_data['total'] = optional + recommended + critical
        self.total = self.total + row_data['total']
        row_data['accumulated_total'] = self.total
        row_data['date'] = str(date1)
        row_data['optional'] = optional
        row_data['critical'] = critical
        row_data['recommended'] = recommended
        #for i in row_pkg:
        #    row_data[i[1].lower()] = i[0]
        self.optional += row_data['optional']
        self.recommended += row_data['recommended']
        self.critical += row_data['critical']
        row_data['accumulated_optional'] = self.optional
        row_data['accumulated_recommended'] = self.recommended
        row_data['accumulated_critical'] = self.critical
        self.data.append(row_data)


class GetTagPackageSeverityOverTimeHandler(BasePackageSeverityOverTimeHandler):
    @authenticated_request
    def post(self):
        super(GetNodePackageSeverityOverTimeHandler,self).post()


class GetNodePackageSeverityOverTimeHandler(BasePackageSeverityOverTimeHandler):
    @authenticated_request
    def post(self):
        super(GetNodePackageSeverityOverTimeHandler,self).post()


class GetPackageSeverityOverTimeHandler(BasePackageSeverityOverTimeHandler):
    @authenticated_request
    def post(self):
        super(GetNodePackageSeverityOverTimeHandler,self).post()


