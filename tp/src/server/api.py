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
from sqlalchemy.orm import sessionmaker, class_mapper


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
        db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
        db.echo = True
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
                               "os_version_mayor" : u[1].os_version_major,
                               "os_version_minor" : u[1].os_version_minor,
                               "os_version_build" : u[1].os_version_build,
                               "os_meta" : u[1].os_meta,
                               "installed" : u[2].patches_installed,
                               "available" : u[2].patches_available,
                               "pending" : u[2].patches_pending,
                               "failed" : u[2].patches_failed})
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))


class NetworkHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
        db.echo = True
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(NetworkStats).all():
            resultjson.append({"key" : "installed", "data" : u.patches_installed})
            resultjson.append({"key" : "available", "data" : u.patches_available})
            resultjson.append({"key" : "pending", "data" : u.patches_pending})
            resultjson.append({"key" : "failed", "data" : u.patches_failed})
        print resultjson
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class PatchHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
        db.echo = True
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(WindowsUpdate).all():
            print u
            resultjson.append({"reference" : {
                "toppatch" : u.toppatch_id,
                "developer" : u.vendor_id
            },
            "date" : str(u.date_pub),
           "name" : u.title,
           "description" : u.description,
           "severity" : u.severity})
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))

class SummaryHandler(BaseHandler):

    @authenticated_request
    def get(self):
        root = {}
        resultjson = []
        osResult = []
        osTypeResult = []
        nodeResult = []
        nodeResult = []
        db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
        db.echo = True
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(SystemInfo.os_code).distinct().all():
            osTypeResult = []
            for v in session.query(SystemInfo.os_string).filter(SystemInfo.os_code == u.os_code).distinct().all():
                nodeResult = []
                for w in session.query(NodeInfo, SystemInfo, NodeStats).join(SystemInfo).join(NodeStats).filter(SystemInfo.os_string == v.os_string).distinct().all():
                    print w
                    nodeResult.append({"name" : w[0].id,
                                       "children" : [{"name" : "Patches Installed", "size" : w[2].patches_installed},
                                           {"name" : "Patches Available", "size" : w[2].patches_available},
                                           {"name" : "Patches Pending", "size" : w[2].patches_pending},
                                           {"name" : "Patches Failed", "size" : w[2].patches_failed}]})
                osTypeResult.append({"name" : v.os_string, "children" : nodeResult})
            osResult.append({"name" : u.os_code, "children" : osTypeResult})
        print resultjson
        root = {"name" : "192.168.1.0", "children" : osResult }
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(root, indent=4))

