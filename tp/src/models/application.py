"""
Classes to help with the CPE specs. http://cpe.mitre.org/specification/index.html, http://nvd.nist.gov/cpe.cfm.

Full version:
               [part="o",vendor="microsoft",product="windows_vista",version="6\.0", update="sp1",edition=NA,language=NA,
                        sw_edition="home_premium", target_sw=NA,target_hw="x64",other=NA]

                Drawing a line at edition. Nothing passed that is checked.

Random example:
        "cpe:/a:activestate:activeperl:5.8.3:NA"
                    |           |       |
                vendor      product     version and upate

    Implementation using here:

        One "Vendor" has many "Product"s which can have many "Version"s
                        |                           |
                    one to many                 one to many


"""

from base import Base
from cve import Cve

from sqlalchemy import String, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref


class Vendor(Base):
    """
    Quick definition of a vendor from CPE specs.
    """
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    products = relationship("Product", backref="vendors")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Vendor('%s','Products: %s')>" % (self.name, self.products)


class Product(Base):
    """
    Definition of the product.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    vendor_id = Column(Integer,ForeignKey("vendors.id"))

    versions = relationship("Version", backref="products")


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Product('%s','Version: %s')>" % (self.name, self.versions)

class Version(Base):
    """
    Rest of the other data: version, update, etc, associated with a product.
    """
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(128))
    update = Column(String(32))
    edition = Column(String(32))

    cves = relationship("Cve", backref="versions")

    product_id = Column(Integer, ForeignKey('products.id'))


    def __init__(self, version, update, edition):
        self.version = version
        self.update = update
        self.edition = edition

    def __repr__(self):
        return "<Version('%s','%s','%s)>" % (self.version, self.update, self.edition)