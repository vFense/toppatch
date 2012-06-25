"""
Classes that help with loading xml data and parsing the file while handing off entry items to there respected individual
entry class. And keeping a collection of those objects.

Example: nvd12345.xml

    <nvd ...>       // <-This is the root of the entire tree for and NVD xml file.

        <entry id="CVE-2011-1759">      // <- tree has various entry items with respected data. collections pass this
            ....                        // and let individual class parse the rest.
        </entry>

    </nvd>
"""

from lxml import objectify

from xml.nvddata import NVDEntry


class NvdCollection():
    """
    Collection class for the NVD xml file. (http://nvd.nist.gov/download.cfm)
    """

    def __init__(self, data):
        self._tree = objectify.parse(data)
        self._root = self._tree.getroot() # <nvd>
        self._entries = self._root.entry # raw lxml collection of <entry> items

        self._entry_list = []

    def parse_collection(self):

        """
        Adds parsed entries (of NveEntry type) to a list and returns it.
        """
        for i in range(len(self._entries)):
            self._entry_list.append(NVDEntry(self._entries[i]))

        return self._entry_list


