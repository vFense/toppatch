"""
Parse the CPE dictionary. Basically a list of vendors and apps with respecting versions.

WARNING: BIG FILE!!! May freeze simple text editors!!!

        http://static.nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.2.xml
"""


"""
The following are constant strings to help with xml namespaces for accessing each xml node.
    By using these strings, we are able to do:

        root[vuln+"vulnerable-configuration"]

    Instead of:

        root["{http://scap.nist.gov/schema/vulnerability/0.4}vulnerable-configuration"]

    all over the place!
"""
_meta_ns		= "{http://scap.nist.gov/schema/cpe-dictionary-metadata/0.2}"


class CpeItem():

    """
    Class describing the 'cpe-item'.

    <cpe-item name="cpe:/a:1024cms:1024_cms:0.7">

        <title xml:lang="en-US">1024cms.org 1024 CMS 0.7</title>
        <meta:item-metadata modification-date="2010-12-14T19:38:32.197Z" status="DRAFT" nvd-id="121218" />

    </cpe-item>
    """

    # Constants to help with split the string name. Don't care (yet) about the first two elements 'cpe' and '\*'.
    vendor = 2
    product = 3
    version = 4
    update = 5
    edition = 6


    def __init__(self, item):
        """
        item should be a namedtuple of CpeMeta = namedtuple("CpeMeta", "valid, name") type.
        """
        self._item = item.name
        self._valid = item.valid
        self._split_item_name()


    def _split_item_name(self):
        """
        Helper for splitting the 'name' item of a 'cpe-item':

            "cpe:/a:1024cms:1024_cms:0.7:update:edition"

        And setting it to respected names.
        """

        self._cpe_name_list = self._item.split(':')

    def get_vendor(self):
        return self._cpe_name_list[CpeItem.vendor]

    def get_product(self):
        return self._cpe_name_list[CpeItem.product]

    def get_version(self):
        if len(self._cpe_name_list) >= (CpeItem.version  + 1): # How can a version not be provided...
            return self._cpe_name_list[CpeItem.version]
        else:
            return "--"

    def get_update(self):
        if len(self._cpe_name_list) >= (CpeItem.update + 1): # Check if there is an update is provided.
            return self._cpe_name_list[CpeItem.update]
        else:
            return "--"

    def get_edition(self):
        if len(self._cpe_name_list) >= (CpeItem.edition + 1): # Check if there is an edition is provided.
            return self._cpe_name_list[CpeItem.edition]
        else:
            return "--"

    def get_modified_date(self):
        return self._item[_meta_ns + 'item-metadata'].get('modification-date')

    def get_status(self):
        return self._item[_meta_ns + 'item-metadata'].get('status')

    def get_validity(self):
        return self._valid

