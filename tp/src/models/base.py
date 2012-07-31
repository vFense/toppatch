from sqlalchemy import String, Integer, Boolean, Column, Text, ForeignKey
from sqlalchemy.orm import relationship, backref

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
