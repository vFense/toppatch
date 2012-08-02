from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from models.scanner import *

class Comparer():
    """ The grand "Comparer" class. Compares data from the 'products'/'cves' table against the 'apps_list' table, determining
    what vulnerabilities, if any, affect the node network.

    End data is stored in the 'vulnerabilities' table.
    """

    MASTER_UPDATE = 0
    NODE_UPDATE = 1

    def __init__(self):
        self._db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
        Session = sessionmaker(bind=self._db)
        self._session = Session()

    def run(self, update_type, time_start=None, time_end=None):
        """ Starts the whole comparer algorithm.

        If update_type = MASTER_UPDATE, then the master server has updated the cves.
        Otherwise if its NODE_UPDATE, the scanner/client (aka agent) might have data on newly installed apps/nodes.
        """

        if update_type == Comparer.MASTER_UPDATE:
            """ Check CVEs """
            pass

        elif update_type == Comparer.NODE_UPDATE:
            """ Check for any new apps/versions/nodes that might have been installed. """
            new_apps = self._session.query(App).filter_by(last_scan_time=time_end).all()
            return new_apps