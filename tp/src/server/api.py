"""Hopefully, this is a RESTful implementation of the Top Patch API."""

import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options


from models.application import *

class ApiHandler(tornado.web.RequestHandler):
    """ Trying to figure out this whole RESTful api thing with json."""

    def get(self, vendor=None, product=None):
        self.session = self.application.session

        root_json = {}

        if vendor and product:
            root_json["vendor"] = vendor
            root_json["product"] = product

            p = self._get_product(vendor, product)
            v_list = []
            for v in p.versions:

                v_list.append(str(v.version) + ":" + str(v.update) + ":" + str(v.edition))

            root_json["versions"] = v_list

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
        self.write(json.dumps(root_json, indent=4))

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

    def _get_cves(self, vendor, product):
        """ Returns list of all CVEs for 'product' from 'vendor'. """




