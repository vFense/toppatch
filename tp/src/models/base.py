from sqlalchemy import String, Integer, Boolean, Column, ForeignKey
#from sqlalchemy.orm import relationship, backref

"""
Base class used by all models. Better than having this simple line of code in all model classes.
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Vulnerability(Base):
    """ Represents one row from the 'vulnerabilities' table.

    Latest known vulnerability in the network. Once the client server compares the CVE data and the scanned apps of each
    node, the results are stored here.

    One vulnerability contains:

        - application affected
        - application version
        - CVE (which in turn can access the refs, score, etc)
        - node it belongs to (ip address and/or hostname)
        - fixed status(whether or not the vulnerability has been resolved. True or False)

        - date found - date which the vulnerability was first discovered on this node.
        - date fixed - date which the vulnerability was resolved.
    """
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True)
    fixed = Column(Boolean)

    cve = Column(Integer, ForeignKey('cves.id'))
    application = Column(Integer, ForeignKey("products.id"))
    version = Column(Integer, ForeignKey("versions.id"))

    node = Column(Integer, ForeignKey("nodes.id"))

    def __init__(self, app_id, cve_id, version_id, node_id, fixed ):

        self.application = app_id
        self.version = version_id
        self.node = node_id
        self.cve = cve_id

        self.fixed = fixed

