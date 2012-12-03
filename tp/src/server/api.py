"""Hopefully, this is a RESTful implementation of the Top Patch API."""

import tornado.httpserver
import tornado.web

try: import simplejson as json
except ImportError: import json

from models.application import *
from server.decorators import authenticated_request
from server.handlers import BaseHandler
from models.base import Base
from models.packages import *
from models.node import *
from models.ssl import *
from server.handlers import SendToSocket
from db.client import *
from scheduler.jobManager import job_lister, remove_job
from scheduler.timeBlocker import *
from tagging.tagManager import *
from search.search import *
from packages.pkgManager import *
from node.nodeManager import *
from transactions.transactions_manager import *
from sqlalchemy import distinct, func
from sqlalchemy.orm import sessionmaker, class_mapper

from jsonpickle import encode


class ApiHandler(BaseHandler):
    """ Trying to figure out this whole RESTful api thing with json."""

    @authenticated_request
    def get(self, vendor=None, product=None):
        self.session = self.application.session
        self.session = validate_session(self.session)
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
        self.session = validate_session(self.session)
        if name:
            return self.session.query(Vendor).filter(Vendor.name == name).first()
        else:
            return self.session.query(Vendor).all()

    def _get_product(self, vendor, product):
        """ Returns specified 'product' from 'vendor'."""
        self.session = validate_session(self.session)

        return self.session.query(Product).join(Vendor).filter(Vendor.name == vendor).filter(Product.name == product).\
        filter(Vendor.id == Product.vendor_id).first()

    def _get_products(self, vendor):
        """ Returns all products from 'vendor'. """
        self.session = validate_session(self.session)

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
        self.session = validate_session(self.session)
        for u in self.session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo, NodeStats):
            print u
            resultjson.append({"id" : u[0].id,
                               "host_name" : u[0].host_name,
                               "display_name" : u[0].display_name,
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
        self.session = validate_session(self.session)
        for u in self.session.query(NetworkStats).all():
            resultjson.append({"key" : "installed", "data" : u.patches_installed})
            resultjson.append({"key" : "available", "data" : u.patches_available})
            resultjson.append({"key" : "pending", "data" : u.patches_pending})
            resultjson.append({"key" : "failed", "data" : u.patches_failed})
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

#class PatchHandler(BaseHandler):
#
#    @authenticated_request
#    def get(self):
#        resultjson = []
#        try:
#            type = self.get_argument('type')
#        except:
#            type = None
#        else:
#            pass
#        session = validate_session(self.application.session)
#        if type == 'available':
#            for u in self.session.query(WindowsUpdate).all():
#                noderesult = []
#                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == False).join(WindowsUpdate).all():
#                    for j in self.session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
#                        noderesult.append(j.ip_address)
#                if len(noderesult) != 0:
#                    resultjson.append({"reference" : {
#                        "toppatch" : u.toppatch_id,
#                        "developer" : u.vendor_id
#                    },
#                   "date" : str(u.date_pub),
#                   "name" : u.name,
#                   "description" : u.description,
#                   "severity" : u.severity,
#                   "node": noderesult})
#        elif type == 'pending':
#            pass
#        elif type == 'installed':
#            for u in self.session.query(WindowsUpdate).all():
#                noderesult = []
#                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id, ManagedWindowsUpdate.installed == True).join(WindowsUpdate).all():
#                    for j in self.session.query(NodeInfo).filter(NodeInfo.id == v.node_id).all():
#                        noderesult.append(j.ip_address)
#                if len(noderesult) != 0:
#                    resultjson.append({"reference" : {
#                        "toppatch" : u.toppatch_id,
#                        "developer" : u.vendor_id
#                    },
#                   "date" : str(u.date_pub),
#                   "name" : u.name,
#                   "description" : u.description,
#                   "severity" : u.severity,
#                   "node": noderesult})
#        elif type == 'failed':
#            pass
#        else:
#            for u in self.session.query(WindowsUpdate).all():
#                nodeAvailable = []
#                nodeInstalled = []
#                nodePending = []
#                nodeFailed = []
#                for v in self.session.query(ManagedWindowsUpdate).filter(ManagedWindowsUpdate.toppatch_id == u.toppatch_id).all():
#                    if v.installed:
#                        nodeInstalled.append(v.node_id)
#                    else:
#                        nodeAvailable.append(v.node_id)
#                resultjson.append({"reference" : {
#                    "toppatch" : u.toppatch_id,
#                    "developer" : u.vendor_id},
#                "date" : str(u.date_pub),
#                "name" : u.name,
#                "description" : u.description,
#                "severity" : u.severity,
#                "available": nodeAvailable,
#                "installed": nodeInstalled,
#                "pending": nodePending,
#                "failed": nodeFailed})
#        self.session.close()
#        self.set_header('Content-Type', 'application/json')
#        self.write(json.dumps(resultjson, indent=4))

class SummaryHandler(BaseHandler):

    @authenticated_request
    def get(self):
        osResult = []
        session = self.application.session
        session = validate_session(session)
        for u in session.query(SystemInfo.os_code).distinct().all():
            osTypeResult = []
            for v in session.query(SystemInfo.os_string).filter(SystemInfo.os_code == u.os_code).distinct().all():
                nodeResult = []
                for w in session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).filter(SystemInfo.os_string == v.os_string).distinct().all():
                    nodeResult.append({"name" : w[0].ip_address,
                                       "children" : [{"name" : "Patches Installed", "size" : w[2].patches_installed},
                                           {"name" : "Patches Available", "size" : w[2].patches_available},
                                           {"name" : "Patches Pending", "size" : w[2].patches_pending},
                                           {"name" : "Patches Failed", "size" : w[2].patches_failed}]})
                osTypeResult.append({"name" : v.os_string, "children" : nodeResult})
            osResult.append({"name" : u.os_code, "children" : osTypeResult})
        root = {"name" : "192.168.1.0", "children" : osResult }
        session.close()
        self.set_header('Content-Type', 'application/json')
        print json.dumps(root, indent=4)
        self.write(json.dumps(root))


class GraphHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        osType = []
        self.session = self.application.session
        self.session = validate_session(self.session)
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
        self.session = validate_session(self.session)
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
        self.session = validate_session(self.session)
        try:
            id = self.get_argument('id')
        except:
            id = None
        if id:
            for u in self.session.query(NodeInfo, SystemInfo).filter(SystemInfo.node_id == id).join(SystemInfo):
                installed = []
                failed = []
                pending = []
                available = []

                for v in self.session.query(PackagePerNode, Package).join(Package).filter(PackagePerNode.node_id == u[1].node_id).all():
                    if v[0].installed:
                        installed.append({'name': v[1].name, 'id': v[0].toppatch_id})
                    elif v[0].pending:
                        pending.append({'name': v[1].name, 'id': v[0].toppatch_id})
                    elif v[0].attempts > 0:
                        failed.append({'name': v[1].name, 'id': v[0].toppatch_id})
                        available.append({'name': v[1].name, 'id': v[0].toppatch_id})
                    else:
                        available.append({'name': v[1].name, 'id': v[0].toppatch_id})
                tags = map(lambda x: x[1].tag, self.session.query(TagsPerNode, TagInfo).join(TagInfo).filter(TagsPerNode.node_id == u[1].node_id).all())
                resultjson = {'ip': u[0].ip_address,
                              'host/name': u[0].host_name,
                              'display/name': u[0].display_name,
                              'host/status': u[0].host_status,
                              'agent/status': u[0].agent_status,
                              'reboot': u[0].reboot,
                              'id': u[1].node_id,
                              'tags': tags,
                              'os/name':u[1].os_string,
                              'os_code': u[1].os_code,
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
                filter = self.get_argument('filterby', default=None)
            except:
                queryCount = 10
                queryOffset = 0
                filter = None

            nodes_query = self.session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats)

            if filter is not None:
                nodes_query = nodes_query.join(TagsPerNode).join(TagInfo).filter(TagInfo.tag == filter)

            for u in nodes_query.limit(queryCount).offset(queryOffset):
                resultnode = {'ip': u[0].ip_address,
                              'hostname': u[0].host_name,
                              'displayname': u[0].display_name,
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

            count = nodes_query.count()
            resultjson = {"count": count, "nodes": data}

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
        self.session = validate_session(self.session)
        try:
            id = self.get_argument('id')
        except:
            id = None
        try:
            type = self.get_argument('type')
        except:
            type = None
        if id:
            for u in self.session.query(Package).filter(Package.toppatch_id == id).all():
                nodeAvailable = []
                nodeInstalled = []
                nodePending = []
                nodeFailed = []
                countAvailable = 0
                countInstalled = 0
                countFailed = 0
                countPending = 0
                for v in self.session.query(PackagePerNode, NodeInfo).filter(PackagePerNode.toppatch_id == u.toppatch_id).join(NodeInfo).all():
                    if v[0].installed:
                        countInstalled += 1
                        nodeInstalled.append({'id': v[0].node_id, 'ip': v[1].host_name})
                    elif v[0].pending:
                        countPending += 1
                        nodePending.append({'id': v[0].node_id, 'ip': v[1].host_name})
                    elif v[0].attempts > 0:
                        countFailed += 1
                        nodeFailed.append({'id': v[0].node_id, 'ip': v[1].host_name})
                        countAvailable += 1
                        nodeAvailable.append({'id': v[0].node_id, 'ip': v[1].host_name})
                    else:
                        countAvailable += 1
                        nodeAvailable.append({'id': v[0].node_id, 'ip': v[1].host_name})
                resultjson = {
                    "name" : u.name,
                    "type": "Security Patch",             #forcing Patch into type
                    "vendor" : {
                        "patchID" : '',         #forcing empty string in patchID
                        "name" : u.vendor_id
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
            query_count = self.session.query(func.count(PackagePerNode.toppatch_id))
            query = self.session.query(PackagePerNode)
            if type:
                if type == 'available':
                    count += self.session.query(func.count(distinct(PackagePerNode.toppatch_id))).filter(PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                    for u in query.filter(PackagePerNode.installed == False, PackagePerNode.pending == False).group_by(PackagePerNode.toppatch_id).limit(queryCount).offset(queryOffset).all():

                        countAvailable = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                        countInstalled = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == True).first()[0]
                        countPending = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                        countFailed = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]

                        for v in self.session.query(Package).filter(Package.toppatch_id == u.toppatch_id).all():
                            result = self._json_results(v.vendor_id, v.toppatch_id, v.date_pub, v.name, v.description,
                                v.severity, countAvailable, countInstalled, countPending, countFailed)
                            data.append(result)

                elif type == 'installed':
                    count += self.session.query(func.count(distinct(PackagePerNode.toppatch_id))).filter(PackagePerNode.installed == True).first()[0]
                    for u in query.filter(PackagePerNode.installed == True).group_by(PackagePerNode.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                        countInstalled = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == True).first()[0]
                        countPending = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                        countFailed = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]

                        for v in self.session.query(Package).filter(Package.toppatch_id == u.toppatch_id).all():
                            result = self._json_results(v.vendor_id, v.toppatch_id, v.date_pub, v.name, v.description,
                                v.severity, countAvailable, countInstalled, countPending, countFailed)
                            data.append(result)

                elif type == 'pending':
                    count += self.session.query(func.count(distinct(PackagePerNode.toppatch_id))).filter(PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                    for u in query.filter(PackagePerNode.installed == False, PackagePerNode.pending == True).group_by(PackagePerNode.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                        countInstalled = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == True).first()[0]
                        countPending = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                        countFailed = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]

                        for v in self.session.query(Package).filter(Package.toppatch_id == u.toppatch_id).all():
                            result = self._json_results(v.vendor_id, v.toppatch_id, v.date_pub, v.name, v.description,
                                v.severity, countAvailable, countInstalled, countPending, countFailed)
                            data.append(result)

                elif type == 'failed':
                    count += self.session.query(func.count(distinct(PackagePerNode.toppatch_id))).filter(PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]
                    for u in query.filter(PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).group_by(PackagePerNode.toppatch_id).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                        countInstalled = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == True).first()[0]
                        countPending = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                        countFailed = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]

                        for v in self.session.query(Package).filter(Package.toppatch_id == u.toppatch_id).all():
                            result = self._json_results(v.vendor_id, v.toppatch_id, v.date_pub, v.name, v.description,
                                v.severity, countAvailable, countInstalled, countPending, countFailed)
                            data.append(result)
                else:
                    count += self.session.query(func.count(Package.severity)).filter(Package.severity == type).first()[0]
                    for u in self.session.query(Package).filter(Package.severity == type).limit(queryCount).offset(queryOffset).all():
                        countAvailable = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False).first()[0]
                        countInstalled = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == True).first()[0]
                        countPending = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == True).first()[0]
                        countFailed = query_count.filter(PackagePerNode.toppatch_id == u.toppatch_id, PackagePerNode.installed == False, PackagePerNode.pending == False, PackagePerNode.attempts > 0).first()[0]


                        result = self._json_results(u.vendor_id, u.toppatch_id, u.date_pub, u.name, u.description,
                            u.severity, countAvailable, countInstalled, countPending, countFailed)
                        data.append(result)

            else:
                for u in self.session.query(Package).order_by(Package.date_pub).limit(queryCount).offset(queryOffset):
                    nodeAvailable = []
                    nodeInstalled = []
                    nodePending = []
                    nodeFailed = []
                    countAvailable = 0
                    countInstalled = 0
                    countFailed = 0
                    countPending = 0

                    for v in self.session.query(PackagePerNode).filter(PackagePerNode.toppatch_id == u.toppatch_id).all():
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

                    result = self._json_results(u.vendor_id, u.toppatch_id, u.date_pub, u.name, u.description,
                        u.severity, countAvailable, countInstalled, countPending, countFailed)
                    data.append(result)

                    for u in self.session.query(func.count(Package.toppatch_id)):
                        count = u[0]
            resultjson = {"count": count, "data": data}
        self.session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

    def _json_results(self, vendor, toppatch_id, date_pub, name, description, severity,
                      available=0, installed=0, pending=0, failed=0):

        data = {"vendor" :
                    {
                        "patchID" : '',         #forcing empty string in patchID
                        "name" : vendor
                    },
                    "type": "Security Patch",             #forcing Patch into type
                    "id": toppatch_id,
                    "date" : str(date_pub),
                    "name" : name,
                    "description" : description.decode('raw_unicode_escape'),
                    "severity" : severity,
                    "nodes/need": available,
                    "nodes/done": installed,
                    "nodes/pend": pending,
                    "nodes/fail": failed}

        return data

class SeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        session = self.application.session
        session = validate_session(session)

        for u in session.query(Package.severity).distinct().all():
            count = 0
            for v in session.query(Package.severity).filter(Package.severity == u.severity).all():
                count += 1

            result_json = { 'label' : str(u.severity), 'value' : count }
            result.append(result_json)

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class CsrHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        self.session = self.application.session
        self.session = validate_session(self.session)
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
        self.session = validate_session(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SchedulerListerHandler(BaseHandler):

    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        result = job_lister(self.session, self.sched)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TimeBlockerListerHandler(BaseHandler):

    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        result = time_block_lister(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class SchedulerAddHandler(BaseHandler):

    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong argument passed %s, the arguement needed is operation" % (e))
        result = job_scheduler(self.msg, self.sched)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class SchedulerRemoveHandler(BaseHandler):

    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        self.sched = self.application.scheduler
        jobname = None
        try:
            jobname = self.get_argument('jobname')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is jobname" % (e))
        result = remove_job(self.sched, jobname)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TimeBlockerAddHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is operation" % (e))
        result = time_block_adder(self.session, self.msg)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class TimeBlockerRemoverHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        tbid = None
        label = None
        startdate = None
        starttime = None
        try:
            tbid = self.get_argument('id')
            result = time_block_remover(self.session, tbid)
        except Exception as e:
            pass
        try:
            label = self.get_argument('label')
            start_date = self.get_argument('start_date')
            start_time = self.get_argument('start_time')
            result = time_block_remover(self.session, label, 
                    start_date, start_time)
        except Exception as e:
            pass
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



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
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_adder(self.session, self.msg)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TagAddPerNodeHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_add_per_node(self.session, self.msg)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TagRemovePerNodeHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_remove_per_node(self.session, self.msg)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class TagRemoveHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        try:
            self.msg = self.get_argument('operation')
        except Exception as e:
            self.write("Wrong arguement passed %s, the argument needed is tag" % (e))
        result = tag_remove(self.session, self.msg)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

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

class GetTagStatsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        tag_id = None
        tag_name = None
        try:
            tag_id = self.get_argument('tagid')
            tag_name = self.get_argument('tagname')
        except Exception as e:
            pass
        result = get_tag_stats(self.session, tagid=tag_id, tagname=tag_name)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class GetTagsPerTpIdHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        tpid = None
        try:
            tpid = self.get_argument('tpid')
        except Exception as e:
            pass
        result = list_tags_per_tpid(self.session, tpid)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



class ModifyDisplayNameHandler(BaseHandler):
    @authenticated_request
    def post(self):
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
                    node.display_name = displayname
                    self.session.commit()
                    result = {"pass" : True,
                              "message" : "Display name change to %s" %\
                                            (displayname)
                            }
                except Exception as e:
                    self.session.rollback()
                    print e.message
                    result = {"pass" : False,
                              "message" : "Display name was not changed to %s"%\
                                            (displayname)
                            }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class ListUserHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        userlist = self.session.query(User).all()
        result = []
        if userlist:
            for user in userlist:
                result.append({"username" : user.username,
                               "id" : user.id
                              })
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class DeleteUserHandler(BaseHandler):
    @authenticated_request
    def post(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        user = None
        userid = None
        username = None
        result = None
        try:
            userid = self.get_argument('userid')
        except Exception as e:
            try:
                username = self.get_argument('username')
            except Exception as e:
                result = {"pass" : False, "message" : \
                            "either pass userid or username"
                         }
        if userid:
            user = self.session.query(User).\
                    filter(User.id == userid).first()
        elif username:
            user = self.session.query(User).\
                    filter(User.username == username).first()
        if user:
            try:
                if user.id != 1:
                    self.session.delete(user)
                    self.session.commit()
                    result = {"pass" : True,
                              "message" : "%s user deleted" % \
                                              (user.username)
                             }
                else:
                    result = {"pass" : False,
                              "message" : "%s user could not be deleted" % \
                                              (user.username)
                             }
            except Exception as e:
                self.session.rollback()
                result = {"pass" : False,
                          "message" : "%s user could not be deleted" % \
                                          (user.username)
                         }
        else:
            result = {"pass" : False,
                      "message" : "%s user does not exist" % \
                                     (user.username)
                         }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


