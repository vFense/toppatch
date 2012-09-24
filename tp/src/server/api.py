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
from models.nodes import *
from sqlalchemy.orm import sessionmaker, class_mapper

from collections import OrderedDict

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




def asdict(obj):
    return dict((col.name, getattr(obj, col.name))
        for col in class_mapper(obj.__class__).mapped_table.c)

class TestHandler(BaseHandler):

    @authenticated_request
    def get(self):
        resultjson = []
        db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
        db.echo = True
        Session = sessionmaker(bind=db)
        session = Session()
        for u in session.query(NodeInfo):#.id, NodeInfo.host_name, NodeInfo.ip_address, NodeInfo.os_code, NodeInfo.os_string, NodeInfo.os_version_major, NodeInfo.os_version_minor, NodeInfo.os_version_build, NodeInfo.os_meta, NodeInfo.host_status, NodeInfo.agent_status):#, NodeInfo.last_agent_update, NodeInfo.last_node_update):
            print u
            resultjson.append({"id" : u.id})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
            resultjson.append({"host_name" : u.host_name})
        print resultjson
        self.session = self.application.session
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(resultjson, indent=4))




