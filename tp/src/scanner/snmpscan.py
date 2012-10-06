
import netsnmp

class snmpScan():
    """A Base Class For a SNMP Session"""
    def __init__(self,
                oid="sysDescr",
                Version=2,
                DestHost="localhost",
                Community="public"):

        self.oid = oid
        self.Version = Version
        self.DestHost = DestHost
        self.Community = Community


    def query(self):
        """Creates SNMP query session"""
        try:
            result = netsnmp.snmpwalk(self.oid,
                 Version = self.Version,
                 DestHost = self.DestHost,
                 Community = self.Community)
        except:
            import sys
            print sys.exc_info()
            result = None

        return result
