from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from models.scanner import *
from models.application import *
from models.base import Vulnerability

class Comparer():
    """ The grand "Comparer" class. Compares data from the 'products'/'cves' table against the 'apps_list' table, determining
    what vulnerabilities, if any, affect the node network.

    End data is stored in the 'vulnerabilities' table.
    """

    MASTER = 0
    NODE = 1

    def __init__(self):
        self._db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
        Session = sessionmaker(bind=self._db)
        self._session = Session()

    def run(self, update_type, scan_date=None):
        """ Starts the whole comparer algorithm.

        If update_type = MASTER_UPDATE, then the master server has updated the cves.
        Otherwise if its NODE_UPDATE, the scanner/client (aka agent) might have data on newly installed apps/nodes.
        """

        if update_type == Comparer.MASTER:
            """ Check CVEs """
            pass

        elif update_type == Comparer.NODE:
            """ Check for any new apps/versions/nodes that might have been installed. """

            node_apps = self._session.query(NodeApp).filter_by(last_scan_date=scan_date).all()
            print "******** Last scanned apps *******"
            print node_apps
            print "**********************************"

            self.search_for_cve(node_apps)

    def search_for_cve(self, node_apps):
        """ 'node_apps' is a list of 'NodeApp' object that is compared against the cve table.

        Checks the app name and version, then gets the cve's accordingly.
        """
        for na in node_apps:
            print na.app.name
            product = self._session.query(Product).filter_by(name=na.app.name).first()
            print product.name

            if product is not None:

                version = self._session.query(Version).join(Product).filter(Product.name==na.app.name).\
                filter(Version.version==na.app.version).first()

                self.save_vulnerability(product, version, na.node)

    def save_vulnerability(self, product, version, node):
        vul = Vulnerability(product.id, version.id, node.id)
        self._session.add(vul)
        self._session.commit()

