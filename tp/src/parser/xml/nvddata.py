"""
    Helper class for the NVD xml files. Holds one entry from that file. (http://nvd.nist.gov/download.cfm)
"""

from lxml import objectify
from collections import namedtuple
"""
    The following are constant strings to help with xml namespaces for accessing each xml node. NDV files "abuse" them! ;)
    By using these strings, we are able to do:

        root[vuln+"vulnerable-configuration"]

    Instead of:

        root["{http://scap.nist.gov/schema/vulnerability/0.4}vulnerable-configuration"]

    all over the place!
"""
_cvss_ns		= "{http://scap.nist.gov/schema/cvss-v2/0.2}"
_cpe_lang_ns 	= "{http://cpe.mitre.org/language/2.0}" 
_patch_ns		= "{http://scap.nist.gov/schema/patch/0.1}"
_xsi_ns			= "{http://www.w3.org/2001/XMLSchema-instance}"
_scap_core_ns	= "{http://scap.nist.gov/schema/scap-core/0.1}"
_vuln_ns		= "{http://scap.nist.gov/schema/vulnerability/0.4}"


""" 
    A little more help for accessing child nodes is always good! Following strings combine xml namespaces with known xml node names found in
    the NVD xml files.  (http://nvd.nist.gov/download.cfm) Obviously better than hardcoded strings everywhere.
"""

_config			= _vuln_ns 		+ "vulnerable-configuration"
_logical_test	= _cpe_lang_ns	+ "logical-test"
_fact_ref		= _cpe_lang_ns 	+ "fact-ref"
_software_list	= _vuln_ns		+ "vulnerable-software-list"
_product		= _vuln_ns		+ "product"
_pub_date		= _vuln_ns		+ "published-datetime"
_mod_date		= _vuln_ns		+ "last-modified-datetime"
_cvss			= _vuln_ns		+ "cvss"
_references		= _vuln_ns		+ "references"

"""	Namedtuple to help with Common Vulnerability Scoring System (CVSS) """
CVScore = namedtuple("CVScore",
    'score, access_vector, access_complexity, authentication, confidentiality_impact, integrity_impact, \
     availability_impact, source, generated_date')

""" Namedtuple to help with references. """
Reference = namedtuple("Reference", "type, source, link, description")

class NVDEntry():
    """
        Helper class for the NVD xml files. Holds one entry from that file. (http://nvd.nist.gov/download.cfm)
    """

    def __init__(self, entry):
        self._entry = entry

    def get_cvss(self):
        """
            Returns a namedtuple of CVScore.
        """
        cvss = self._entry[_cvss][_cvss_ns + "base_metrics"]

        score			= cvss[_cvss_ns + "score"]
        vector			= cvss[_cvss_ns + "access-vector"]
        complexity		= cvss[_cvss_ns + "access-complexity"]
        auth		 	= cvss[_cvss_ns + "authentication"]
        confi			= cvss[_cvss_ns + "confidentiality-impact"]
        integrity 		= cvss[_cvss_ns + "integrity-impact"]
        avali 			= cvss[_cvss_ns + "availability-impact"]
        src 			= cvss[_cvss_ns + "source"]
        date 			= cvss[_cvss_ns + "generated-on-datetime"]

        metrics = CVScore(score, vector, complexity, auth, confi, integrity, avali, src, date)

        return metrics

    def get_cwe_id(self):
        return self._entry[_vuln_ns + "cwe"].get("id")

    def get_cve_id(self):
        return self._entry[_vuln_ns + "cve-id"]

    def get_published_date(self):
        return self._entry[_pub_date]

    def get_modified_date(self):
        return self._entry[_mod_date]

    def get_summary(self):
        return self._entry[_vuln_ns + "summary"]

    def get_vulnerable_list(self):
        """
            Returns a list of vulnerable software and version.
        """
        l = []
        software_list = self._entry[_software_list].product

        for i in range(len(software_list)):
            app = software_list[i]

            l.append(app)

        return l


    def get_references(self):
        """
            Returns a list of 'Reference' (namedtuple) type.
            Reference = namedtuple("Reference", "type, source, link, description")
        """
        l = []
        refs = self._entry[_references]

        for i in range(len(refs)):
            t = refs[i].get("reference_type")
            src = refs[i][_vuln_ns + "source"]
            link = refs[i][_vuln_ns + "reference"].get("href")
            description = refs[i][_vuln_ns + "reference"]

            l.append(Reference(t, src, link, description))

        return l


if __name__ == "__main__":
    data = NVDEntry()
    print data.get_vulnerable_list()



















