"CVE DOWNLOADER FOR TOPPATCH"

import os, sys
from datetime import date
import requests

tmp_path = os.path.join\
        (os.path.dirname(os.path.abspath(__file__)), '../data/xml')

start_year = 2002
iter_year = start_year
current_year = date.today().year
url_path = 'http://static.nvd.nist.gov/feeds/xml/cve/'
nvdcve_modified = 'nvdcve-2.0-modified.xml'
nvd_modified_url = url_path + nvdcve_modified
nvd_modified_path = tmp_path + '/' + nvdcve_modified
nvdcve = 'nvdcve-2.0-'

def cve_downloader(cve_url, cve_path):
    r = requests.get(cve_url)
    xml = open(cve_path, 'wb')
    if r.ok:
        xml.write(r.content)
    return(r.ok, os.stat(cve_path).st_size)

def print_status(status, size, url_path, nvd_path):
    if status == True and size > 0:
        print '%s Downloaded to %s' % ( url_path, nvd_path )
    elif xml_status[0] == False:
        print '%s Could not be downloaded' % ( url_path )
    else:
        print '%s Was downloaded to %s, but the size is %d' \
                % ( url_path, nvd_path, size )

mod_xml = cve_downloader(nvd_modified_url, nvd_modified_path)
print_status(mod_xml[0], mod_xml[1], \
        nvd_modified_url, nvd_modified_path)

while iter_year <= current_year:
    nvd = nvdcve + str(iter_year) + '.xml'
    full_url =  url_path + nvd
    full_nvd = os.path.join(tmp_path, nvd)
    if not os.path.exists(full_nvd):
        xml_status = cve_downloader(full_url, full_nvd)
        print_status(xml_status[0], xml_status[1], full_url, full_nvd)
    else:
        print "%s already exists at %s" % ( nvd, full_nvd )
    iter_year = iter_year + 1
