"""Hopefully, this is a RESTful implementation of the Top Patch API."""

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


class PatchesHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        patch_oper = re.compile(r'installed|available|pending|failed')
        patch_sev = re.compile(r'Critical|Optional|Recommended')
        queryCount = 10
        queryOffset = 0
        tpid = None
        pstatus = None
        try:
            tpid = self.get_argument('id')
        except:
            pass
        try:
            queryCount = self.get_argument('count')
            queryOffset = self.get_argument('offset')
        except:
            pass
        try:
            pstatus = self.get_argument('type')
        except:
            pass
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


class SslHandler(BaseHandler):
    @authenticated_request
    def get(self):
        result = []
        self.session = self.application.session
        self.session = validate_session(self.session)
        for u in self.session.query(SslInfo, NodeInfo).join(NodeInfo).all():
            result.append({'enabled': u[0].enabled,
                'node_id': u[0].node_id,
                'ip': u[1].ip_address
                })
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
