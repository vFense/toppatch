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




class NodesHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = []
        self.session = self.application.session
        self.session = validate_session(self.session)
        node_id = self.get_argument('id', None)
        queryCount = self.get_argument('count', 10)
        queryOffset = self.get_argument('offset', 0)
        filter_by_tags = self.get_argument('filterby', None)
        query = None
        if filter_by_tags:
            query = self.session.query(NodeInfo, SystemInfo, NodeStats).\
                    join(SystemInfo, NodeStats,TagsPerNode, TagInfo).\
                    filter(TagInfo.tag == filter_by_tags).\
                    limit(queryCount).offset(queryOffset).all()
        else:
            query = self.session.query(NodeInfo, SystemInfo, NodeStats).\
                    join(SystemInfo, NodeStats).limit(queryCount).\
                    offset(queryOffset)
        if node_id:
            for node_info in self.session.query(NodeInfo, SystemInfo,\
                    NetworkInterface).filter(SystemInfo.node_id == node_id).\
                    join(SystemInfo, NetworkInterface):
                installed = []
                failed = []
                pending = []
                available = []
                net = []
                if len(node_info) >=3:
                    net_info = node_info[2]
                    for net in net_info:
                        if net.node_id:
                            network = {
                                    'interface_name': net.interface,
                                    'mac': net.mac_address,
                                    'ip': net.ip_address
                                    }
                            net.append(network)
                for pkg in self.session.query(PackagePerNode, Package).\
                        join(Package).filter(PackagePerNode.node_id \
                        == node_info[1].node_id).all():
                    if pkg[0].installed:
                        installed.append({'name': pkg[1].name,
                            'id': pkg[0].toppatch_id,
                            'severity': pkg[1].severity
                            })
                    elif pkg[0].pending:
                        pending.append({'name': pkg[1].name,
                            'id': pkg[0].toppatch_id,
                            'severity': pkg[1].severity
                            })
                    elif pkg[0].attempts > 0:
                        failed.append({'name': pkg[1].name,
                            'id': pkg[0].toppatch_id,
                            'severity': pkg[1].severity
                            })
                        available.append({'name': pkg[1].name,
                            'id': pkg[0].toppatch_id,
                            'severity': pkg[1].severity
                            })
                    else:
                        available.append({'name': pkg[1].name,
                            'id': pkg[0].toppatch_id,
                            'severity': pkg[1].severity
                            })
                tags = map(lambda x: x[1].tag,
                        self.session.query(TagsPerNode, TagInfo).\
                                join(TagInfo).\
                                filter(TagsPerNode.node_id == \
                                node_info[1].node_id).all()
                                )
                resultjson = {'ip': node_info[0].ip_address,
                              'host/name': node_info[0].host_name,
                              'display/name': node_info[0].display_name,
                              'host/status': node_info[0].host_status,
                              'agent/status': node_info[0].agent_status,
                              'networking': net,
                              'reboot': node_info[0].reboot,
                              'id': node_info[1].node_id,
                              'tags': tags,
                              'os/name':node_info[1].os_string,
                              'os_code': node_info[1].os_code,
                              'patch/need': available,
                              'patch/done': installed,
                              'patch/fail': failed,
                              'patch/pend': pending
                               }
            print resultjson
            print "foo"
            if len(resultjson) == 0:
                resultjson = {'error' : 'no data to display'}
        else:
            data = []
            count = 0
            print query
            for node_info in query:
                resultnode = {'ip': node_info[0].ip_address,
                              'hostname': node_info[0].host_name,
                              'displayname': node_info[0].display_name,
                              'host/status': node_info[0].host_status,
                              'agent/status': node_info[0].agent_status,
                              'reboot': node_info[0].reboot,
                              'id': node_info[1].node_id,
                              'os/name':node_info[1].os_string,
                              'patch/need': node_info[2].patches_available,
                              'patch/done': node_info[2].patches_installed,
                              'patch/fail': node_info[2].patches_failed,
                              'patch/pend': node_info[2].patches_pending
                               }
                data.append(resultnode)
            count = query.count()
            resultjson = {"count": count, "nodes": data}
            print resultjson
            print "ROO"
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))



class NodeTogglerHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        userlist = self.session.query(User).all()
        nodeid = self.get_argument('nodeid', None)
        toggle = self.get_argument('toggle', None)
        if toggle:
            toggle = return_bool(toggle)
        if nodeid:
            sslinfo = self.session.query(SslInfo).\
                    filter(SslInfo.node_id == nodeid).first()
            if sslinfo:
                if toggle:
                    sslinfo.enabled = True
                    self.session.commit()
                    logger.info('%s - ssl communication for nodeid %s '%\
                            (username, nodeid) + 'has been enabled'
                           ) 
                    result = {"pass" : True,
                          "message" : "node_id %s has been enabled" %\
                                          (nodeid)
                         }
                else:
                    sslinfo.enabled = False
                    self.session.commit()
                    logger.info('%s - ssl communication for nodeid %s '%\
                            (username, nodeid) + 'has been disabled'
                           ) 
                    result = {"pass" : True,
                          "message" : "node_id %s has been disabled" %\
                                          (nodeid)
                         }
        else:
            logger.warn('%s - invalid nodeid %s' % (username, nodeid))
            result = {"pass" : False,
                      "message" : "node_id %s does not exist" % \
                                     (nodeid)
                         }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))
