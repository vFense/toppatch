from parser.collections import CpeCollection
from parser.xml.cpedata import CpeItem

collections = CpeCollection("data/cpe.xml")
items = collections.parse_collection()

for i in range(len(items)):

    print "Vendor: " + items[i].get_vendor()
    print "Product: " + items[i].get_product()
    print "Version: " + items[i].get_version()
    print "Update: " + items[i].get_update()
    print "Mod Date: " + items[i].get_modified_date()
    print "Status: " + items[i].get_status()
    print "+-----------------------------------+"
