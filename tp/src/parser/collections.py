"""
Classes that help with loading xml data and parsing the file while handing off entry items to there respected individual
entry class. And keeping a collection of those objects.
"""

from lxml import objectify

from xml.nvddata import NvdEntry
from xml.cpedata import CpeItem


class NvdCollection():
    """
    Collection class for the NVD xml file. (http://nvd.nist.gov/download.cfm)
    Example: nvd12345.xml

    <nvd ...>       // <-This is the root of the entire tree for and NVD xml file.

        <entry id="CVE-2011-1759">      // <- tree has various entry items with respected data. collections pass this
            ....                        // and let individual class parse the rest.
        </entry>

    </nvd>
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
            self._entry_list.append(NvdEntry(self._entries[i]))

        return self._entry_list


class CpeCollection():
    """
    Collection of 'cpe-item's.
    <cpe-item name="cpe:/a:1024cms:1024_cms:0.7">
        ...
    </cpe-item>
    """
    def __init__(self, data):
        self._tree = objectify.parse(data)
        self._root = self._tree.getroot() # <cpe-list>
        self._generator = self._root.generator

        # Unfortunately, CPE has names in the XML file that use a dash ('-'), hence not python friendly.
        # Had to look up the attribute using __dict__. Python kicks ass!
        self._items = self._root.__dict__['cpe-item'] # raw lxml collection of <cpe-item> items

        self._entry_list = []

    def parse_collection(self):

        """
        Adds parsed entries (of CpeItem type) to a list and returns it.
        Have to ignore the first item in the list because its of type

        <generator>
            ...
        </generator>

        Ignore for now.

        """
        for i in range(len(self._items)):
            print "Item #: " + str(i)
            self._entry_list.append(CpeItem(self._items[i]))

        return self._entry_list
