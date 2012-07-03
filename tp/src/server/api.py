"""
Hopefully, this is a RESTful implementation of the Top Patch API.
"""

import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

# Quick hack to include app modules
import os, sys
p = os.path.abspath('./src')
sys.path.append(p)
from models.application import *

class ApiHandler(tornado.web.RequestHandler):
    def get(self, vendor=None):
        session = self.application.session
        self.set_header('Content-Type', 'application/json')

        if vendor:
            all_products = {}
            product_list = session.query(Product).join(Vendor).filter(Vendor.name == vendor).\
            filter(Vendor.id == Product.vendor_id).all()

            products = []
            for product in product_list:
                products.append(product.name)

            all_products["vendor"] = vendor
            all_products["products"] = products

            self.write(json.dumps(all_products, indent=4))

        else:
            all_vendors = {}
            vendor_list = session.query(Vendor).all()
            vendors = []
            for vendor in vendor_list:
                vendors.append(vendor.name)

            all_vendors["vendors"] = vendors
            self.write(json.dumps(all_vendors, indent=4))
