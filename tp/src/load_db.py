from sqlalchemy.engine import *
from sqlalchemy.orm import *

from parser.xml.nvddata import NVDEntry
from parser.collections import NvdCollection

from models.cve import Cve, Cvss, Reference
from models.base import Base

__author__ = 'Miguel Moll'


db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)
session = Session()

nc = NvdCollection("./data/nvdcve-2.0-recent.xml")
entries = nc.parse_collection()

for i in range(len(entries)):

    cvss = entries[i].get_cvss()
    refs = entries[i].get_references()


    cve = Cve(entries[i].get_cve_id(), entries[i].get_cwe_id(), entries[i].get_published_date(),
                entries[i].get_modified_date(), entries[i].get_summary())

    cve.cvss = Cvss(cvss.score, cvss.access_vector,
        cvss.access_complexity, cvss.authentication,
        cvss.confidentiality_impact, cvss.integrity_impact,
        cvss.availability_impact, cvss.source, cvss.generated_date)

    cve.refs = []
    refs = entries[i].get_references()

    for i in range(len(refs)):
        r = Reference(refs[i].type, refs[i].source, refs[i].link, refs[i].description)
        cve.refs.append(r)

    session.add(cve)

session.commit()

