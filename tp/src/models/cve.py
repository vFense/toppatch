"""
Various helper/model classes used for sqlalchemy.
"""

from models.base import Base

from sqlalchemy import String, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref

class Cve(Base):
    """
    Defines Common Vulnerabilities and Exposures (CVE) table named 'cves'. Also python helper class to interface with sai
    table.
    """
    __tablename__ = "cves"

    id = Column(Integer, primary_key=True)
    cve_id = Column(String(20))
    cwe_id = Column(String(10))
    pub_date = Column(String(35))
    mod_date = Column(String(35))
    summary = Column(Text)

    cvss = relationship("Cvss", uselist=False, backref="cves")

    def __init__(self, cve_id, cwe_id, pdate, mdate, summary):
        self.cve_id = cve_id
        self.cwe_id = cwe_id
        self.pub_date = pdate
        self.mod_date = mdate
        self.summary = summary

    def __repr__(self):
        return "<CVE('%s', '%s')>" % (self.cve_id, self.summary)

class Cvss(Base):
    """
    Class representing Common Vulnerability Scoring System (CVSS)
    http://nvd.nist.gov/cvss.cfm
    """
    __tablename__ = "cvss"

    id = Column(Integer, primary_key=True)
    score = Column(String(5))
    access_vector = Column(String(10))
    access_complexity = Column(String(10))
    authentication = Column(String(10))
    confidentiality = Column(String(10))
    integrity_impact = Column(String(10))
    availability_impact = Column(String(10))
    source = Column(Text)
    generated_date = Column(String(35))

    cve_id = Column(Integer, ForeignKey('cves.id') )

    def __init__(self, score, av, ac, auth, confid, ii, ai, src, gd):
        """
        Ugly param names. Basically shorthand/initials for class variables.
        """
        self.score = score
        self.access_vector = av
        self.access_complexity = ac
        self.authentication = auth
        self.confidentiality = confid
        self.integrity_impact = ii
        self.availability_impact = ai
        self.source = src
        self.generated_date = gd


class Reference(Base):
    """
    Represents the 'reference' data associated with a CVE. ie: Links to patches, reading material, etc.

    Basic namedtuble to pass data around:
        Reference = namedtuple("Reference", "type, source, link, description")
    """
    __tablename__ = "refs"

    id = Column(Integer, primary_key=True)
    type = Column(String(15))
    source = Column(String(15))
    link = Column(Text)
    description = Column(Text)

    cve_id = Column(Integer, ForeignKey('cves.id') )
    cve = relationship("Cve", backref=backref('refs', order_by=id))

    def __init__(self, type, source, link, desc):
        self.type = type
        self.source = source
        self.link = link
        self.description = desc
