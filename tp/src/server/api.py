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
from models.ssl import *
from server.handlers import SendToSocket
from utils.db.client import *
from utils.scheduler.jobManager import jobLister
from utils.scheduler.timeBlocker import *
from sqlalchemy import distinct, func
from sqlalchemy.orm import sessionmaker, class_mapper


class ApiHandler(BaseHandler):
    """ Trying to figure out this whole RESTful api thing with json."""

    @authenticated_request
    def get(self, vendor=None, product=None):
        self.session = self.application.session
        self.session = validateSession(self.session)
        root_json = {}
        if vendor and product:
            root_json["vendor"] = vendor
            root_json["product"] = product
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
        self.session = validateSession(self.session)
        if name:
            return self.session.query(Vendor).filter(Vendor.name == name).first()
        else:
            return self.session.query(Vendor).all()

    def _get_product(self, vendor, product):
        """ Returns specified 'product' from 'vendor'."""
        self.session = validateSession(self.session)

        return self.session.query(Product).join(Vendor).filter(Vendor.name == vendor).filter(Product.name == product).\
        filter(Vendor.id == Product.vendor_id).first()

    def _get_products(self, vendor):
        """ Returns all products from 'vendor'. """
        self.session = validateSession(self.session)

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
        self.session = self.application.session
        self.session = validateSession(self.session)
        for u in self.session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo, NodeStats):
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
        self.session.close()
        SendToSocket('hi')
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))


class NetworkHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        for u in self.session.query(NetworkStats).all():
            resultjson.append({"key" : "installed", "data" : u.patches_installed})
            resultjson.append({"key" : "available", "data" : u.patches_available})
            resultjson.append({"key" : "pending", "data" : u.patches_pending})
            resultjson.append({"key" : "failed", "data" : u.patches_failed})
        self.session.close()
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
        self.session = self.application.session
        self.session = validateSession(self.session)
        if type == 'available':
            for u in self.session.query(WindowsUpdate).all():
                noderesult = []
                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False).join(WindowsUpdate).all():
                    for j in self.session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
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
            for u in self.session.query(WindowsUpdate).all():
                noderesult = []
                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).join(WindowsUpdate).all():
                    for j in self.session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
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
            for u in self.session.query(WindowsUpdate).all():
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).all():
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
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SummaryHandler(BaseHandler):

    @authenticated_request
    def get(self):
        root = {}
        resultjson = []
        osResult = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        for u in self.session.query(SystemInfo.os_code).distinct().all():
            osTypeResult = []
            for v in self.session.query(SystemInfo.os_string).filter(SystemInfo.os_code == u.os_code).distinct().all():
                nodeResult = []
                for w in self.session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).filter(SystemInfo.os_string == v.os_string).distinct().all():
                    print w
                    nodeResult.append({"name" : w[0].ip_address,
                                       "children" : [{"name" : "Patches Installed", "size" : w[2].patches_installed},
                                           {"name" : "Patches Available", "size" : w[2].patches_available},
                                           {"name" : "Patches Pending", "size" : w[2].patches_pending},
                                           {"name" : "Patches Failed", "size" : w[2].patches_failed}]})
                osTypeResult.append({"name" : v.os_string, "children" : nodeResult})
            osResult.append({"name" : u.os_code, "children" : osTypeResult})
        root = {"name" : "192.168.1.0", "children" : osResult }
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(root, indent=4))


class GraphHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        osType = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        for u in self.session.query(SystemInfo.os_string, func.count(SystemInfo.os_string)).group_by(SystemInfo.os_string).all():
            nodeResult = []
            for v in self.session.query(NodeInfo, SystemInfo, NodeStats).filter(SystemInfo.os_string == u[0]).join(SystemInfo).join(NodeStats).all():
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
        self.session = validateSession(self.session)
        for u in self.session.query(NodeInfo, SystemInfo, NodeStats).filter(SystemInfo.os_string == type).join(SystemInfo).join(NodeStats).all():
            installed += u[2].patches_installed
            available += u[2].patches_available
            pending += u[2].patches_pending
            failed += u[2].patches_failed
        if installed or available or pending or failed:
            resultjson.append({"label" : "Installed", "value" : installed})
            resultjson.append({"label" : "Available", "value" : available})
            resultjson.append({"label" : "Pending", "value" : pending})
            resultjson.append({"label" : "Failed", "value" : failed})
            self.session.close()
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson, indent=4))
        else:
            self.session.close()
            resultjson = {'error' : 'no data to display'}
            self.write(json.dumps(resultjson, indent=4))

class NodesHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        try:
            id = self.get_argument('id')
        except:
            id = None
        else:
            pass
        if id:
            for u in self.session.query(NodeInfo, SystemInfo).filter(SystemInfo.node_id == id).join(SystemInfo):
                installed = []
                failed = []
                pending = []
                available = []
                for v in self.session.query(ManagedWindowsUpdate, WindowsUpdate).join(WindowsUpdate).filter(ManagedWindowsUpdate.node_id == u[1].node_id).all():
                    if v[0].installed:
                        installed.append({'name': v[1].title, 'id': v[0].toppatch_id})
                    elif v[0].pending:
                        pending.append({'name': v[1].title, 'id': v[0].toppatch_id})
                    elif v[0].attempts > 0:
                        failed.append({'name': v[1].title, 'id': v[0].toppatch_id})
                        available.append({'name': v[1].title, 'id': v[0].toppatch_id})
                    else:
                        available.append({'name': v[1].title, 'id': v[0].toppatch_id})
                resultjson = {'ip': u[0].ip_address,
                              'host/name': u[0].host_name,
                              'host/status': u[0].host_status,
                              'agent/status': u[0].agent_status,
                              'reboot': u[0].reboot,
                              'id': u[1].node_id,
                              'tags': [],
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
            for u in self.session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).limit(queryCount).offset(queryOffset):
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
            for u in self.session.query(func.count(SystemInfo.node_id)):
                count = u
            resultjson = {"count": count[0], "nodes": data}
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class PatchesHandler(BaseHandler):

    @authenticated_request
    def get(self):
        data = []
        resultjson = {}
        count = 0
        self.session = self.application.session
        self.session = validateSession(self.session)
        try:
            id = self.get_argument('id')
        except:
            id = None
        try:
            type = self.get_argument('type')
        except:
            type = None
        if id:
            for u in self.session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == id).all():
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                countAvailable = 0
                countInstalled = 0
                countFailed = 0
                countPending = 0
                for v in self.session.query(ManagedWindowsUpdate, NodeInfo).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).join(NodeInfo).all():
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
                    "size" : u.file_size,
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
            query_count = self.session.query(func.count(distinct(ManagedWindowsUpdate.toppatch_id)))
            query = self.session.query(ManagedWindowsUpdate)
            if type:
                if type == 'available':
                    count = query_count.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                    for u in query.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).group_by(ManagedWindowsUpdate.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                        countInstalled = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).first()[0]
                        countPending = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                        countFailed = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]

                        for v in self.session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == u.toppatch_id).all():
                            data.append({"vendor" : {
                                "patchID" : '',         #forcing empty string in patchID
                                "name" : 'Microsoft'    #forcing microsoft on all patch names
                            },
                             "type": "Security Patch",             #forcing Patch into type
                             "id": v.toppatch_id,
                             "date" : str(v.date_pub),
                             "name" : v.title,
                             "description" : v.description,
                             "severity" : v.severity,
                             "nodes/need": countAvailable,
                             "nodes/done": countInstalled,
                             "nodes/pend": countPending,
                             "nodes/fail": countFailed,
                             "nodes": []})
                elif type == 'installed':
                    count = query_count.filter(ManagedWindowsUpdate.installed == True).first()[0]
                    for u in query.filter(ManagedWindowsUpdate.installed == True).group_by(ManagedWindowsUpdate.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                        countInstalled = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).first()[0]
                        countPending = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                        countFailed = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]

                        for v in self.session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == u.toppatch_id).all():
                            data.append({"vendor" : {
                                "patchID" : '',         #forcing empty string in patchID
                                "name" : 'Microsoft'    #forcing microsoft on all patch names
                            },
                             "type": "Security Patch",             #forcing Patch into type
                             "id": v.toppatch_id,
                             "date" : str(v.date_pub),
                             "name" : v.title,
                             "description" : v.description,
                             "severity" : v.severity,
                             "nodes/need": countAvailable,
                             "nodes/done": countInstalled,
                             "nodes/pend": countPending,
                             "nodes/fail": countFailed,
                             "nodes": []})
                elif type == 'pending':
                    count = query_count.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                    for u in query.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).group_by(ManagedWindowsUpdate.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                        countInstalled = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).first()[0]
                        countPending = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                        countFailed = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]

                        for v in self.session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == u.toppatch_id).all():
                            data.append({"vendor" : {
                                "patchID" : '',         #forcing empty string in patchID
                                "name" : 'Microsoft'    #forcing microsoft on all patch names
                            },
                             "type": "Security Patch",             #forcing Patch into type
                             "id": v.toppatch_id,
                             "date" : str(v.date_pub),
                             "name" : v.title,
                             "description" : v.description,
                             "severity" : v.severity,
                             "nodes/need": countAvailable,
                             "nodes/done": countInstalled,
                             "nodes/pend": countPending,
                             "nodes/fail": countFailed,
                             "nodes": []})
                elif type == 'failed':
                    count = query_count.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]
                    for u in query.filter(ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).group_by(ManagedWindowsUpdate.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                        countInstalled = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).first()[0]
                        countPending = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                        countFailed = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]

                        for v in self.session.query(WindowsUpdate).filter(WindowsUpdate.toppatch_id == u.toppatch_id).all():
                            data.append({"vendor" : {
                                "patchID" : '',         #forcing empty string in patchID
                                "name" : 'Microsoft'    #forcing microsoft on all patch names
                            },
                             "type": "Security Patch",             #forcing Patch into type
                             "id": v.toppatch_id,
                             "date" : str(v.date_pub),
                             "name" : v.title,
                             "description" : v.description,
                             "severity" : v.severity,
                             "nodes/need": countAvailable,
                             "nodes/done": countInstalled,
                             "nodes/pend": countPending,
                             "nodes/fail": countFailed,
                             "nodes": []})
                else:
                    count = self.session.query(func.count(WindowsUpdate.severity)).filter(WindowsUpdate.severity == type).first()[0]
                    for u in self.session.query(WindowsUpdate).filter(WindowsUpdate.severity == type).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False).first()[0]
                        countInstalled = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).first()[0]
                        countPending = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == True).first()[0]
                        countFailed = query_count.filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False, ManagedWindowsUpdate.pending == False, ManagedWindowsUpdate.attempts > 0).first()[0]
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
                        "nodes": []})

            else:
                for u in self.session.query(WindowsUpdate).order_by(WindowsUpdate.date_pub).limit(queryCount).offset(queryOffset):
                    nodeAvailable = []
                    nodeInstalled = []
                    nodePending = []
                    nodeFailed = []
                    countAvailable = 0
                    countInstalled = 0
                    countFailed = 0
                    countPending = 0

                    for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).all():
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
                    for u in self.session.query(func.count(WindowsUpdate.toppatch_id)):
                        count = u[0]
            resultjson = {"count": count, "data": data}
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        resultjson = {}
        result = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        for u in self.session.query(WindowsUpdate.severity).distinct().all():
            count = 0
            for v in self.session.query(WindowsUpdate).filter(WindowsUpdate.severity == u.severity).all():
                count += 1
                print v
            print u
            resultjson = { 'label' : str(u.severity), 'value' : count }
            result.append(resultjson)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class CsrHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        self.session = self.application.session
        self.session = validateSession(self.session)
        try:
            signed = self.get_argument('signed')
            is_signed = True if signed == 'true' or signed == 'True' else  False
        except:
            signed = None
            is_signed = None
        if signed:
            for u in self.session.query(SslInfo, CsrInfo, NodeInfo).join(CsrInfo).join(NodeInfo).filter(CsrInfo.is_csr_signed == is_signed).all():
                result.append({'signed': u[1].is_csr_signed, 'node_id': u[0].node_id, 'ip': u[2].ip_address})
        else:
            for u in self.session.query(SslInfo, CsrInfo, NodeInfo).join(CsrInfo).join(NodeInfo).all():
                result.append({'signed': u[1].is_csr_signed, 'node_id': u[0].node_id, 'ip': u[2].ip_address})
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class UserHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = {"name" : self.current_user}
        self.session = self.application.session
        self.session = validateSession(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SchedulerListerHandler(BaseHandler):

    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validateSession(self.session)
        self.sched = self.application.scheduler
        result = jobLister(self.session, self.sched)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TimeBlockerListerHandler(BaseHandler):

    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validateSession(self.session)
        self.sched = self.application.scheduler
        result = timeBlockLister(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class SchedulerAddHandler(BaseHandler):

    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validateSession(self.session)
        self.sched = self.application.scheduler
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the arguement needed is operation" % (e))
        result = JobScheduler(self.msg, self.sched)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TimeBlockerAddHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validateSession(self.session)
        self.sched = self.application.scheduler
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is operation" % (e))
        print type(self.msg), self.msg
        result = timeBlockAdder(self.msg, self.sched)
        self.set_header('Content-Type', 'application/json')
        self.write(result, indent=4)


class OperationHandler(BaseHandler):

    @authenticated_request
    def post(self):
        resultjson = []
        node = {}
        result = []
        try:
            nodes = self.request.arguments['node']
            print nodes
        except:
            nodes = None
        try:
            params = self.get_argument('params')
        except:
            params = None
        try:
            time = self.get_argument('time')
            schedule = self.get_argument('schedule')
        except:
            time = None
            schedule = None
        if nodes:
            operation = self.get_argument('operation')
            if time:
                node['schedule'] = schedule
                node['time'] = time
            if operation == 'install' or operation == 'uninstall':
                patches = self.request.arguments['patches']
                for node_id in nodes:
                    node['node_id'] = node_id
                    node['operation'] = operation
                    node['data'] = list(patches)
                    resultjson.append(encode(node))
                if time:
                    JobScheduler(resultjson, 
                            self.application.scheduler
                            )
                else:
                    operation_runner = AgentOperation(resultjson)
                    operation_runner.run()
            elif operation == 'reboot':
                for node_id in nodes:
                    node['operation'] = operation
                    node['node_id'] = node_id
                    resultjson.append(encode(node))
                if time:
                    JobScheduler(resultjson, 
                            self.application.scheduler
                            )
                else:
                    operation_runner = AgentOperation(resultjson)
                    operation_runner.run()
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson))
        if params:
            resultjson = json.loads(params)
            AgentOperation(resultjson)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson))


