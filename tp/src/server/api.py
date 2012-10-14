"""Hopefully, this is a RESTful implementation of the Top Patch API."""

import tornado.httpserver
import tornado.web

try: import simplejson as json
except ImportError: import json

from models.application import *
from server.decorators import authenticated_request
from server.handlers import BaseHandler
from models.base import Base
from models.windows import *
from models.node import *
from server.handlers import SendToSocket
from sqlalchemy import distinct, func
from sqlalchemy.orm import sessionmaker, class_mapper


db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
db.echo = True

class ApiHandler(BaseHandler):
    """ Trying to figure out this whole RESTful api thing with json."""

    @authenticated_request
    def get(self, vendor=None, product=None):
        self.session = self.application.session

        root_json = {}

        if vendor and product:
            root_json["vendor"] = vendor
            root_json["product"] = product


#            p = self._get_product(vendor, product)
#            v_list = []
#            for v in p.versions:
#                v_list.append(str(v.version) + ":" + str(v.update) + ":" + str(v.edition))

            #root_json["versions"] = v_list
            root_json["versions"] = self._get_cves(vendor, product)

        elif vendor:

            product_list = self._get_products(vendor)

            products = []
            for product in product_list:
                products.append(product.name)

            root_json["vendor"] = vendor
            root_json["products"] = products

        else:
            vendor_list = self._get_vendor()
            vendors = []
            for vendor in vendor_list:
                vendors.append(vendor.name)

            root_json["vendors"] = vendors

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps([root_json], indent=4))

    def _get_vendor(self, name=None):
        """ Returns all vendors (list) if name is None otherwise the vendor 'name'."""
        if name:
            return self.session.query(Vendor).filter(Vendor.name == name).first()
        else:
            return self.session.query(Vendor).all()

    def _get_product(self, vendor, product):
        """ Returns specified 'product' from 'vendor'."""

        return self.session.query(Product).join(Vendor).filter(Vendor.name == vendor).filter(Product.name == product).\
        filter(Vendor.id == Product.vendor_id).first()

    def _get_products(self, vendor):
        """ Returns all products from 'vendor'. """

        return self.session.query(Product).join(Vendor).filter(Vendor.name == vendor).\
        filter(Vendor.id == Product.vendor_id).all()

    def _get_cves(self, vendor, product, version=None):
        """ Returns all the CVEs from 'product' in a list. If version is provided then only CVEs for that version. Otherwise returns
        all CVEs from all versions.
        """
        root_list = []
        root_node = {}



        if version:
            pass
        else:
            prod = self._get_product(vendor, product)

            for v in prod.versions:
                root_node["version"] = str(v.version) + ":" + str(v.update) + ":" + str(v.edition)

                # Create temp files here to clean them after every version.
                cve_list = []
                cve_node = {}

                for c in v.cves:
                    # Deep copy the dicts and lists to prevent reference copies.

                    cve_node["id"] = c.cve_id
                    cve_node["score"] = c.cvss.score

                    # Same method as above
                    refs_list = []
                    refs_node = {}

                    for r in c.refs:
                        refs_node["link"] = r.link
                        refs_node["type"] = r.type

                        refs_list.append(dict(refs_node))
                        cve_node["refs"] = list(refs_list)


                    cve_list.append(dict(cve_node))
                    root_node["cves"] = list(cve_list)

                root_list.append(dict(root_node))

        return root_list

class NodeHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo, NodeStats):
            print u
            resultjson.append({"id" : u[0].id,
                               "host_name" : u[0].host_name,
                               "ip_address" : u[0].ip_address,
                               "host_status" : u[0].host_status,
                               "agent_status" : u[0].agent_status,
                               "os_code" : u[1].os_code,
                               "os_string" : u[1].os_string,
                               #"os_version_mayor" : u[1].os_version_major,
                               #"os_version_minor" : u[1].os_version_minor,
                               #"os_version_build" : u[1].os_version_build,
                               #"os_meta" : u[1].os_meta,
                               "installed" : u[2].patches_installed,
                               "available" : u[2].patches_available,
                               "pending" : u[2].patches_pending,
                               "failed" : u[2].patches_failed})
        session.close()
        SendToSocket('hi')
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))


class NetworkHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(NetworkStats).all():
            resultjson.append({"key" : "installed", "data" : u.patches_installed})
            resultjson.append({"key" : "available", "data" : u.patches_available})
            resultjson.append({"key" : "pending", "data" : u.patches_pending})
            resultjson.append({"key" : "failed", "data" : u.patches_failed})
        session.close()
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class PatchHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        try:
            type = self.get_argument('type')
        except:
            type = None
        else:
            pass
        Session = sessionmaker(bind=db)
        session = Session()
        if type == 'available':
            for u in session.query(WindowsUpdate).all():
                noderesult = []
                for v in session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False).join(WindowsUpdate).all():
                    for j in session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
                        noderesult.append(j.ip_address)
                if len(noderesult) != 0:
                    resultjson.append({"reference" : {
                        "toppatch" : u.toppatch_id,
                        "developer" : u.vendor_id
                    },
                   "date" : str(u.date_pub),
                   "name" : u.title,
                   "description" : u.description,
                   "severity" : u.severity,
                   "node": noderesult})
        elif type == 'pending':
            pass
        elif type == 'installed':
            for u in session.query(WindowsUpdate).all():
                noderesult = []
                for v in session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).join(WindowsUpdate).all():
                    for j in session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
                        noderesult.append(j.ip_address)
                if len(noderesult) != 0:
                    resultjson.append({"reference" : {
                        "toppatch" : u.toppatch_id,
                        "developer" : u.vendor_id
                    },
                   "date" : str(u.date_pub),
                   "name" : u.title,
                   "description" : u.description,
                   "severity" : u.severity,
                   "node": noderesult})
        elif type == 'failed':
            pass
        else:
            for u in session.query(WindowsUpdate).all():
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                for v in session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).all():
                    if v.installed:
                        nodeInstalled.append(v.node_id)
                    else:
                        nodeAvailable.append(v.node_id)
                resultjson.append({"reference" : {
                    "toppatch" : u.toppatch_id,
                    "developer" : u.vendor_id},
                "date" : str(u.date_pub),
                "name" : u.title,
                "description" : u.description,
                "severity" : u.severity,
                "available": nodeAvailable,
                "installed": nodeInstalled,
                "pending": nodePending,
                "failed": nodeFailed})
        session.close()
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SummaryHandler(BaseHandler):

    @authenticated_request
    def get(self):
        root = {}
        resultjson = []
        osResult = []
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(SystemInfo.os_code).distinct().all():
            osTypeResult = []
            for v in session.query(SystemInfo.os_string).filter(SystemInfo.os_code == u.os_code).distinct().all():
                nodeResult = []
                for w in session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).filter(SystemInfo.os_string == v.os_string).distinct().all():
                    print w
                    nodeResult.append({"name" : w[0].ip_address,
                                       "children" : [{"name" : "Patches Installed", "size" : w[2].patches_installed},
                                           {"name" : "Patches Available", "size" : w[2].patches_available},
                                           {"name" : "Patches Pending", "size" : w[2].patches_pending},
                                           {"name" : "Patches Failed", "size" : w[2].patches_failed}]})
                osTypeResult.append({"name" : v.os_string, "children" : nodeResult})
            osResult.append({"name" : u.os_code, "children" : osTypeResult})
        root = {"name" : "192.168.1.0", "children" : osResult }
        session.close()
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(root, indent=4))


class GraphHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        osType = []
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(SystemInfo.os_string, func.count(SystemInfo.os_string)).group_by(SystemInfo.os_string).all():
            nodeResult = []
            for v in session.query(NodeInfo, SystemInfo, NodeStats).filter(SystemInfo.os_string == u[0]).join(SystemInfo).join(NodeStats).all():
                nodeResult.append({"name" : v[0].ip_address,
                                   "os" : v[1].os_string,
                                   "children" : [{"name" : "Patches Installed", "size" : v[2].patches_installed, "graphData" : {"label" : v[0].ip_address, "value" : v[2].patches_installed}},
                                                {"name" : "Patches Available", "size" : v[2].patches_available, "graphData" : {"label" : v[0].ip_address, "value" : v[2].patches_available}},
                                                {"name" : "Patches Pending", "size" : v[2].patches_pending, "graphData" : {"label" : v[0].ip_address, "value" : v[2].patches_pending}},
                                                {"name" : "Patches Failed", "size" : v[2].patches_failed, "graphData" : {"label" : v[0].ip_address, "value" : v[2].patches_failed}}]})
            """
            os = str(u[0]).split()
            ostring = ''
            j = 0
            while j < len(os):
                if j < 4:
                    if j == 0 and os[j] == 'Windows':
                        ostring += os[j][:3]
                        ostring += ' '
                    else:
                        ostring += os[j]
                        ostring += ' '
                j += 1
            """
            osType.append({"label" : u[0], "value" : u[1], "data" : nodeResult})
        resultjson = osType
        session.close()
        self.session = self.application.session
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
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(NodeInfo, SystemInfo, NodeStats).filter(SystemInfo.os_string == type).join(SystemInfo).join(NodeStats).all():
            installed += u[2].patches_installed
            available += u[2].patches_available
            pending += u[2].patches_pending
            failed += u[2].patches_failed
        if installed or available or pending or failed:
            resultjson.append({"label" : "Installed", "value" : installed})
            resultjson.append({"label" : "Available", "value" : available})
            resultjson.append({"label" : "Pending", "value" : pending})
            resultjson.append({"label" : "Failed", "value" : failed})
            session.close()
            self.session = self.application.session
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson, indent=4))
        else:
            session.close()
            resultjson = {'error' : 'no data to display'}
            self.write(json.dumps(resultjson, indent=4))

class NodesHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        Session = sessionmaker(bind=db)
        session = Session()
        try:
            id = self.get_argument('id')
        except:
            id = None
        else:
            pass
        if id:
            for u in session.query(NodeInfo, SystemInfo).filter(SystemInfo.node_id == id).join(SystemInfo):
                installed = []
                failed = []
                pending = []
                available = []
                for v in session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.node_id == u[1].node_id).all():
                    if v.installed:
                        installed.append(v.toppatch_id)
                    elif v.pending:
                        pending.append(v.toppatch_id)
                    elif v.attempts > 0:
                        failed.append(v.toppatch_id)
                        available.append(v.toppatch_id)
                    else:
                        available.append(v.toppatch_id)
                resultjson = {'ip': u[0].ip_address,
                              'host/name': u[0].host_name,
                              'host/status': u[0].host_status,
                              'agent/status': u[0].agent_status,
                              'reboot': u[0].reboot,
                              'id': u[1].node_id,
                              'os/name':u[1].os_string,
                              'patch/need': available,
                              'patch/done': installed,
                              'patch/fail': failed,
                              'patch/pend': pending
                               }
            if len(resultjson) == 0:
                resultjson = {'error' : 'no data to display'}
        else:
            data = []
            count = 0
            try:
                queryCount = self.get_argument('count')
                queryOffset = self.get_argument('offset')
            except:
                queryCount = 10
                queryOffset = 0
            for u in session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).limit(queryCount).offset(queryOffset):
                resultnode = {'ip': u[0].ip_address,
                              'host/status': u[0].host_status,
                              'agent/status': u[0].agent_status,
                              'reboot': u[0].reboot,
                              'id': u[1].node_id,
                              'os/name':u[1].os_string,
                              'patch/need': u[2].patches_available,
                              'patch/done': u[2].patches_installed,
                              'patch/fail': u[2].patches_failed,
                              'patch/pend': u[2].patches_pending
                               }
                data.append(resultnode)
            for u in session.query(func.count(SystemInfo.node_id)):
                count = u
            resultjson = {"count": count[0], "nodes": data}
        session.close()
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class PatchesHandler(BaseHandler):

    @authenticated_request
    def get(self):
        data = []
        resultjson = {}
        count = 0
        Session = sessionmaker(bind=db)
        session = Session()
        try:
            id = self.get_argument('id')
        except:
            id = None
        try:
            type = self.get_argument('type')
        except:
            type = None
        if id:
            for u in session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == id).all():
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                countAvailable = 0
                countInstalled = 0
                countFailed = 0
                countPending = 0
                for v in session.query(ManagedWindowsUpdate, NodeInfo).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).join(NodeInfo).all():
                    if v[0].installed:
                        countInstalled += 1
                        nodeInstalled.append({'id': v[0].node_id, 'ip': v[1].ip_address})
                    elif v[0].pending:
                        countPending += 1
                        nodePending.append({'id': v[0].node_id, 'ip': v[1].ip_address})
                    elif v[0].attempts > 0:
                        countFailed += 1
                        nodeFailed.append({'id': v[0].node_id, 'ip': v[1].ip_address})
                        countAvailable += 1
                        nodeAvailable.append({'id': v[0].node_id, 'ip': v[1].ip_address})
                    else:
                        countAvailable += 1
                        nodeAvailable.append({'id': v[0].node_id, 'ip': v[1].ip_address})
                resultjson = {
                    "name" : u.title,
                    "type": "Security Patch",             #forcing Patch into type
                    "vendor" : {
                        "patchID" : '',         #forcing empty string in patchID
                        "name" : 'Microsoft'    #forcing microsoft on all patch names
                    },
                    "id": u.toppatch_id,
                    "severity" : u.severity,
                    "description" : u.description,
                    "date" : str(u.date_pub),
                    "available": {'count' :countAvailable, 'nodes': nodeAvailable},
                    "installed": {'count' :countInstalled, 'nodes': nodeInstalled},
                    "pending": {'count' :countPending, 'nodes': nodePending},
                    "failed": {'count' :countFailed, 'nodes': nodeFailed}
                }
        else:
            try:
                queryCount = self.get_argument('count')
                queryOffset = self.get_argument('offset')
            except:
                queryCount = 10
                queryOffset = 0
            for u in session.query(WindowsUpdate).order_by(WindowsUpdate.date_pub).offset(queryOffset):
                node = []
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                countAvailable = 0
                countInstalled = 0
                countFailed = 0
                countPending = 0

                for v in session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).all():
                    if v.installed:
                        countInstalled += 1
                        nodeInstalled.append(v.node_id)
                    elif v.pending:
                        countPending += 1
                        nodePending.append(v.node_id)
                    elif v.attempts > 0:
                        countFailed += 1
                        nodeFailed.append(v.node_id)
                        countAvailable += 1
                        nodeAvailable.append(v.node_id)
                    else:
                        countAvailable += 1
                        nodeAvailable.append(v.node_id)
                if type:
                    if type == 'available':
                        node = nodeAvailable
                        for j in session.query(func.count(distinct(ManagedWindowsUpdate.toppatch_id))).filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False):
                            count = j[0]
                    elif type == 'installed':
                        node = nodeInstalled
                        for j in session.query(func.count(distinct(ManagedWindowsUpdate.toppatch_id))).filter(ManagedWindowsUpdate.installed == True):
                            count = j[0]
                    elif type == 'pending':
                        node = nodePending
                        for j in session.query(func.count(distinct(ManagedWindowsUpdate.toppatch_id))).filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True):
                            count = j[0]
                    elif type == 'failed':
                        node = nodeFailed
                        for j in session.query(func.count(distinct(ManagedWindowsUpdate.toppatch_id))).filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0):
                            count = j[0]
                    if len(node) > 0:
                        data.append({"vendor" : {
                                        "patchID" : '',         #forcing empty string in patchID
                                        "name" : 'Microsoft'    #forcing microsoft on all patch names
                                      },
                                     "type": "Security Patch",             #forcing Patch into type
                                     "id": u.toppatch_id,
                                     "date" : str(u.date_pub),
                                     "name" : u.title,
                                     "description" : u.description,
                                     "severity" : u.severity,
                                     "nodes/need": countAvailable,
                                     "nodes/done": countInstalled,
                                     "nodes/pend": countPending,
                                     "nodes/fail": countFailed,
                                     "nodes": node})
                else:
                    data.append({"vendor" : {
                                        "patchID" : '',         #forcing empty string in patchID
                                        "name" : 'Microsoft'    #forcing microsoft on all patch names
                                    },
                                   "type": "Security Patch",             #forcing Patch into type
                                   "id": u.toppatch_id,
                                   "date" : str(u.date_pub),
                                   "name" : u.title,
                                   "description" : u.description,
                                   "severity" : u.severity,
                                   "nodes/need": countAvailable,
                                   "nodes/done": countInstalled,
                                   "nodes/pend": countPending,
                                   "nodes/fail": countFailed})
                    for u in session.query(func.count(WindowsUpdate.toppatch_id)):
                        count = u[0]
            resultjson = {"count": count, "data": data}
        session.close()
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = {}
        result = []
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(WindowsUpdate.severity).distinct().all():
            count = 0
            for v in session.query(WindowsUpdate).filter(WindowsUpdate.severity == u.severity).all():
                count += 1
                print v
            print u
            resultjson = { 'label' : str(u.severity), 'value' : count }
            result.append(resultjson)
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class UserHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = {"name" : self.current_user}
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))
