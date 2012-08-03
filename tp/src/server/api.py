"""Hopefully, this is a RESTful implementation of the Top Patch API."""

try: import simplejson as json
except ImportError: import json

from models.application import *
from models.scanner import Vulnerability
from server.decorators import authenticated_request
from server.handlers import BaseHandler

class CveHandler(BaseHandler):
    """ API for CVE data """

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
#                    Don't add refs to the json. To much data. Use api providing the CVE id to get the refs
#                    refs_list = []
#                    refs_node = {}
#
#                    for r in c.refs:
#                        refs_node["link"] = r.link
#                        refs_node["type"] = r.type
#
#                        refs_list.append(dict(refs_node))
#                        cve_node["refs"] = list(refs_list)


                    cve_list.append(dict(cve_node))
                    root_node["cves"] = list(cve_list)

                root_list.append(dict(root_node))

        return root_list


class NodeHandler(BaseHandler):
    """  Data for nodes on the network. """

    @authenticated_request
    def get(self):
        print self.application.session.query(Vulnerability).filter_by(fixed=False).all()

