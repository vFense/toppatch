#!/usr/bin/env python
import re
from models.packages import *
from models.node import *
from utils.common import *
from utils.db.client import validateSession


valid_pkg_columns = {
                     "description" : Package.description,
                     "name" : Package.name,
                     "kb" : Package.kb,
                     "severity" : Package.severity
                     }

is_os = {
        "is_linux" : PackagePerNode.is_linux, 
        "is_windows" : PackagePerNode.is_windows,
        "is_mac" : PackagePerNode.is_mac,
        "is_unix" : PackagePerNode.is_unix,
        "is_bsd" : PackagePerNode.is_bsd
        }

def basicPackageSearch(session, query, column, count=None, offset=None):
    session = validateSession
    query = re.sub(r'^|$', '%', query)
    data = []
    final_out = {}
    total_count = 0
    if column in valid_pkg_columns:
        found_packages = session.query(Package).filter(valid_pkg_columns[description].like(query)).order_by(Package.toppatch_id.desc()).limit(count).offset(offset)
        total_count = session.query(Package).count()
        for pkg in found_packages:
            nodes_done = session.query(PackagePerNode).filter(PackagePerNode.toppatch_id == pkg.toppatch_id).filter(PackagePerNode.installed == True).all()
            nodes_needed = session.query(PackagePerNode).filter(PackagePerNode.toppatch_id == pkg.toppatch_id).filter(PackagePerNode.installed == False).all()
            nodes_pending = session.query(PackagePerNode).filter(PackagePerNode.toppatch_id == pkg.toppatch_id).filter(PackagePerNode.pending == True).all()
            nodes_failed = session.query(PackagePerNode).filter(PackagePerNode.toppatch_id == pkg.toppatch_id).filter(PackagePerNode.attempts >= 1).all()
            data.append({
                "id" : pkg.toppatch_id,
                "date" : pkg.date_published,
                "description" : pkg.description,
                "name" : pkg.name,
                "severity" : pkg.severity,
                "nodes/need" : nodes_needed,
                "nodes/fail" : nodes_failed,
                "nodes/pend" : nodes_pending,
                "nodes/done" : nodes_done,
                "vendor" : {"name" : pkg.vendor_id, "patchID" : ""}
                }
        final_count['count'] = total_count
        final_count['data'] = data
        return final_count


"""def advancePackageSearch(session, query, column, is_installed=None,
                            is_available=None, is_installed=None,
                            is_linux=False, is_windows=False, is_bsd=False,
                            is_unix=False, is_mac=False, all=False):
    session = validateSession
    query = re.sub(r'^|$', '%', query)
    all_packages []
    if all:
        if column in valid_pkg_columns:
            output = session.query(Package).filter(valid_pkg_columns[description].like(query)).all()
"""
