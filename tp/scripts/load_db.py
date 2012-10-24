import os
import subprocess

from sqlalchemy.engine import *
from sqlalchemy.orm import *

from parser.collections import NvdCollection
from parser.xml.cpedata import CpeItem

from models.cve import Cve, Cvss, Reference
from models.application import *

toppatch_dir = '/opt/TopPatch'

mysql_dir = toppatch_dir + '/mysql/current'
mysql_data_dir = mysql_dir + '/data'

nc = NvdCollection("./data/xml/nvd.xml")
entries = nc.parse_collection()

db = None
session = None

"""

def create_cve(entry):
    cvss = entry.get_cvss()


    cve = Cve(entry.get_cve_id(), entry.get_cwe_id(), entry.get_published_date(),
        entry.get_modified_date(), entry.get_summary())

    cve.cvss = Cvss(cvss.score, cvss.access_vector,
        cvss.access_complexity, cvss.authentication,
        cvss.confidentiality_impact, cvss.integrity_impact,
        cvss.availability_impact, cvss.source, cvss.generated_date)

    cve.refs = []
    refs = entry.get_references()

    for i in range(len(refs)):
        r = Reference(refs[i].type, refs[i].source, refs[i].link, refs[i].description)
        cve.refs.append(r)

    return cve

def run():

    load_db = True
    if load_db:
        for x in range(len(entries)):

            software = entries[x].get_vulnerable_software_list()


            for i in range(len(software)):
                cpe = CpeItem(software[i])
                if cpe.get_validity():

                    vendor_name = cpe.get_vendor()
                    product_name = cpe.get_product()
                    version = cpe.get_version()
                    update = cpe.get_update()
                    edition = cpe.get_edition()

                    print "+----------------Begin----------------------------+"
                    print str(vendor_name) + " " + str(product_name) + " " + str(version)  + " " + str(update) + " " + str(edition)
                    print "+-------------------------------------------------+"

                    if session.query(Vendor).filter(Vendor.name == vendor_name).first() is not None: ## Check if vendor exist
                        print "--Vendor Exist."
                        if session.query(Product).join(Vendor).filter(Vendor.name == vendor_name).filter(Product.name == product_name).first() is not None:   # Check if products exist with vendor.
                            print "----Product Exist."

                            if session.query(Product).join(Vendor,Version).filter(Vendor.name == vendor_name).\
                                                                        filter(Product.name == product_name).\
                                                                        filter(Version.version == version).first() is not None: #Check Version
                                print "------Version Exist."

                                if session.query(Product).join(Vendor,Version).filter(Vendor.name == vendor_name).filter(Product.name == product_name).\
                                   filter(Version.version == version).filter(Version.update == update).first() is not None: #Check update
                                    print "--------Update Exist."

                                    if session.query(Product).join(Vendor,Version).filter(Vendor.name == vendor_name).filter(Product.name == product_name).\
                                    filter(Version.version == version).filter(Version.update == update).\
                                       filter(Version.edition == edition).first() is not None: #Check edition
                                        print "** Products + Version already in database. **"
                                        v = session.query(Version,Vendor).join(Product).filter(Vendor.name == vendor_name).filter(Product.name == product_name).\
                                        filter(Version.version == version).filter(Version.update == update).\
                                        filter(Version.edition == edition).first()

                                        # Just add the CVE but should really check if its already included
                                        v = v.Version
                                        v.cves.append(create_cve(entries[x]))
                                    else:
                                        prod = session.query(Product).join(Vendor).filter(Product.name == product_name).first()
                                        print "++Adding version w/ update + edition (" + str(version) + "," + str(update) + "," + str(edition) +  ")."
                                        v = Version(version, update, edition)
                                        v.cves.append(create_cve(entries[x]))
                                        prod.versions.append(v)

                                else:
                                    prod = session.query(Product).join(Vendor).filter(Vendor.name == vendor_name).filter(Product.name == product_name).first()
                                    print "++Adding version w/ update (" + str(version) + "," + str(update) + "," + str(edition) +  ")."
                                    v = Version(version, update, edition)
                                    v.cves.append(create_cve(entries[x]))
                                    prod.versions.append(v)


                            else:
                                prod = session.query(Product).join(Vendor).filter(Vendor.name == vendor_name).filter(Product.name == product_name).first()
                                print "++Adding version (" + str(version) + "," + str(update) + "," + str(edition) +  ")."
                                v = Version(version, update, edition)
                                v.cves.append(create_cve(entries[x]))
                                prod.versions.append(v)

                        else:
                            vendor = session.query(Vendor).filter(Vendor.name == vendor_name).first()
                            print "++Adding product " + str(product_name) + " to vendor " + str(vendor.name) + "."
                            prod = Product(product_name)

                            v = Version(version, update, edition)
                            v.cves.append(create_cve(entries[x]))

                            prod.versions.append(v)
                            vendor.products.append(prod)
                    else:
                        print "++Vendor doesn't exist. Add it all."
                        vendor = Vendor(cpe.get_vendor())
                        prod = Product(cpe.get_product())

                        v = Version(version, update, edition)
                        v.cves.append(create_cve(entries[x]))

                        prod.versions.append(v)
                        vendor.products.append(prod)

                        print vendor
                        session.add(vendor)
    session.commit()

    """

print "Initializing TopPatch Database!"
"""
if os.path.exists(mysql_data_dir):
    print "MySQL data directory present. Connecting..."
    db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch')

else:
"""

print "Creating MySQL data directory."
owd = os.getcwd()
os.chdir(mysql_dir)
print os.getcwd()

subprocess.call(['./scripts/mysql_install_db'])
subprocess.call(['./support-files/mysql.server', 'start'])
subprocess.call(['./bin/mysqladmin', '-u', 'root', 'password', 'topmiamipatch'], )

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/')
db.connect().execute("CREATE DATABASE toppatch_server;")
db.connect().execute("USE toppatch_server;")
os.chdir(owd)

Base.metadata.create_all(db)
#Session = sessionmaker(bind=db)
#session = Session()
#run()
