"CVE DOWNLOADER FOR TOPPATCH"

from datetime import date
import request

tmp_path = ''
start_year = 2002
cur_year = date.today().year
url_path = 'http://static.nvd.nist.gov/feeds/xml/cve/'
nvdcve_modified = 'nvdcve-2.0-modified.xml'
nvdcve_recent = 'nvdcve-2.0-recent.xml'
nvdcve_2002 = 'nvdcve-2.0-2002.xml'
nvdcve_2003 = 'nvdcve-2.0-2003.xml'
nvdcve_2004 = 'nvdcve-2.0-2004.xml'
nvdcve_2005 = 'nvdcve-2.0-2005.xml'
nvdcve_2006 = 'nvdcve-2.0-2006.xml'
