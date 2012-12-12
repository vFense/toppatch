#!/usr/bin/env python
import re
from models.packages import *
from models.node import *
from utils.common import *
from db.client import validate_session


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

def basic_package_search(session, query, column, count=0, offset=0, output="json"):
    """
        This search function, gives you the ability to search by column.
        Search by column ( description|name|kb|severity )
        query == ssh
        column == description
        session == SqlAlchemy session object
        count == How many results do you want in return ( default == all )
        offset == if you want to return only a certain amount of results
        based on a count and an offset
        output == json|csv
    """
    session = validate_session(session)
    query = re.sub(r'^|$', '%', query)
    data = []
    csv_out = ""
    json_out = {}
    total_count = 0
    if column in valid_pkg_columns:
        found_packages = session.query(Package).\
                filter(valid_pkg_columns[column].like(query)).\
                order_by(Package.toppatch_id.desc()).limit(count).\
                offset(offset)
        total_count = session.query(Package).\
                filter(valid_pkg_columns[column].like(query)).\
                order_by(Package.toppatch_id.desc()).count()
        for pkg in found_packages:
            nodes_done = session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).\
                    filter(PackagePerNode.installed == True).count()
            nodes_needed = session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).\
                    filter(PackagePerNode.installed == False).count()
            nodes_pending = session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).\
                    filter(PackagePerNode.pending == True).count()
            nodes_failed = session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).\
                    filter(PackagePerNode.attempts >= 1).count()
            if "json" in output:
                data.append({
                        "id" : pkg.toppatch_id,
                        "date" : str(pkg.date_pub),
                        "description" : pkg.description,
                        "name" : pkg.name,
                        "severity" : pkg.severity,
                        "nodes/need" : nodes_needed,
                        "nodes/fail" : nodes_failed,
                        "nodes/pend" : nodes_pending,
                        "nodes/done" : nodes_done,
                        "vendor" : {"name" : pkg.vendor_id, "patchID" : ""}
                            })
            elif "csv" in output:
                csv_out = csv_out + '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (pkg.name,
                        pkg.description, pkg.toppatch_id, pkg.severity,
                        str(pkg.date_pub), pkg.vendor_id, nodes_needed,
                        nodes_failed, nodes_pending, nodes_done
                        )
        if 'json' in output:
            json_out['count'] = total_count
            json_out['data'] = data
            return json_out
        elif 'csv' in output:
            return csv_out


"""def advancePackageSearch(session, query, column, is_installed=None,
                            is_available=None, is_installed=None,
                            is_linux=False, is_windows=False, is_bsd=False,
                            is_unix=False, is_mac=False, all=False):
    session = validate_session
    query = re.sub(r'^|$', '%', query)
    all_packages []
    if all:
        if column in valid_pkg_columns:
            output = session.query(Package).filter(valid_pkg_columns[description].like(query)).all()
"""