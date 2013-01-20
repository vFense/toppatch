
from time import sleep
from db.query_table import *
from db.update_table import *
from db.client import validate_session



def return_node_json(node):
    return({"node_id": node.id,
            "displayname": node.display_name,
            "hostname": node.host_name,
            "ipaddress": node.ip_address,
            "hoststatus": node.host_status,
            "agentstatus": node.agent_status,
            "reboot": node.reboot
            })


def retrieveDependencies(session, msg):
    session = validate_session
    AgentOperation()
    dep_exists = session.query(LinuxPackageDependency).\
            filter(LinuxPackageDependency.toppatch_id == pkg_id).first()


def list_tags_per_tpid(session, tpid):
    """ 
        Return a json object containing the nodes and the related packages
        concerning that node within the tag name.
        arguments below..
        session == sqlalchemy session object
        tpid == the toppatch_id of the package
    """
    session = validate_session(session)
    tagdict = {}
    tagdict['available'] =[]
    tagdict['pending'] = []
    tagdict['failed'] = []
    tagdict['done'] = []
    tagdict['pass'] = True
    tagdict['message'] = 'Tags found for toppatchid %s' % (tpid)
    tag_pos = {}
    i = 0
    list_of_nodes = session.query(PackagePerNode).\
            filter(PackagePerNode.toppatch_id == tpid).all()
    if len(list_of_nodes) >0:
        for node in list_of_nodes:
            list_of_tags = session.query(TagsPerNode).\
                    filter(TagsPerNode.node_id == node.node_id).all()
            if len (list_of_tags) >0:
                node_info = session.query(NodeInfo).\
                        filter(NodeInfo.id == node.node_id).first()
                tag_nodes = []
                for tagnode in list_of_tags:
                    tag = session.query(TagInfo).\
                            filter(TagInfo.id == tagnode.tag_id).first()
                    if not tag.tag in tag_pos:
                        tag_pos[tag.tag] = i
                        i = i + 1
                    if node.installed:
                        if not tag_pos[tag.tag] in range(len(tagdict['done'])):
                            tagdict['done'].append({'tag_name': tag.tag, 
                                    'tag_id': tag.id,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['done'][tag_pos[tag.tag]]['tag_name']:
                            tagdict['done'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif node.installed and node.pending:
                        if not tag_pos[tag.tag] in range(len(tagdict['pending'])):
                            tagdict['pending'].append({'tag_name': tag.tag,
                                    'tag_id': tag.id,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['pending'][tag_pos[tag.tag]]['tag_name']:
                            tagdict['pending'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif not node.installed and node.attempts >=1:
                        if not tag_pos[tag.tag] in range(len(tagdict['failed'])):
                            tagdict['failed'].append({'tag_name': tag.tag,
                                    'tag_id': tag.id,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['failed'][tag_pos[tag.tag]]['tag_name']:
                            tagdict['failed'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif not node.installed and node.attempts ==0:
                        if not tag_pos[tag.tag] in range(len(tagdict['available'])):
                            tagdict['available'].append({'tag_name': tag.tag,
                                    'tag_id': tag.id,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['available'][tag_pos[tag.tag]]['tag_name']:
                            tagdict['available'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))

        return(tagdict)
    else:
        tagdict['pass'] = False
        tagdict['message'] = 'Tags do not exist for toppatchid %s' % (tpid)
        return(tagdict)


class PatchRetriever():
    """
        Main Class for retrieving package information.
    """
    def __init__(self, session, qcount=20, qoffset=0):
        """
            This must be called first with at least session
            initialized.

            session == SQLAlchemy Session
            qcount == how many results you want to retreive
            qoffset == what is the offset, that you want returned
        """
        self.session = validate_session(session)
        self.qcount = qcount
        self.qoffset = qoffset

    def get_by_toppatch_id(self, tpid):
        """
            retrieve the patch information to a corresponding
            toppatch id
            tpid == valid toppatch_id
        """
        self.tpid = tpid
        pkg = self.session.query(Package).\
                filter(Package.toppatch_id == self.tpid).first()
        if pkg:
            nodeAvailable = []
            nodeInstalled = []
            nodePending = []
            nodeFailed = []
            countAvailable = 0
            countInstalled = 0
            countFailed = 0
            countPending = 0
            pkg_node = self.session.query(PackagePerNode, NodeInfo).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).\
                    join(NodeInfo).all()
            for node in pkg_node:
                if node[0].installed:
                    countInstalled += 1
                    nodeInstalled.append({
                        'id': node[0].node_id,
                        'ip': node[1].ip_address,
                        'hostname': node[1].host_name,
                        'displayname': node[1].display_name
                        })
                elif node[0].pending:
                    countPending += 1
                    nodePending.append({
                        'id': node[0].node_id,
                        'ip': node[1].ip_address,
                        'hostname': node[1].host_name,
                        'displayname': node[1].display_name
                        })
                elif node[0].attempts > 0:
                    countFailed += 1
                    nodeFailed.append({
                        'id': node[0].node_id,
                        'ip': node[1].ip_address,
                        'hostname': node[1].host_name,
                        'displayname': node[1].display_name
                        })
                    countAvailable += 1
                    nodeAvailable.append({
                        'id': node[0].node_id,
                        'ip': node[1].ip_address,
                        'hostname': node[1].host_name,
                        'displayname': node[1].display_name
                        })
                else:
                    countAvailable += 1
                    nodeAvailable.append({
                        'id': node[0].node_id,
                        'ip': node[1].ip_address,
                        'hostname': node[1].host_name,
                        'displayname': node[1].display_name
                        })
                resultjson = {
                    "name" : pkg.name,
                    "type": "Security Patch",
                    "vendor" : {
                        "patchID" : '',
                        "name" : pkg.vendor_id
                    },
                    "id": pkg.toppatch_id,
                    "severity" : pkg.severity,
                    "size" : pkg.file_size,
                    "description" : pkg.description,
                    "date" : str(pkg.date_pub),
                    "available": {'count' :countAvailable,
                        'nodes': nodeAvailable},
                    "installed": {'count' :countInstalled,
                        'nodes': nodeInstalled},
                    "pending": {'count' :countPending,
                        'nodes': nodePending},
                    "failed": {'count' :countFailed,
                        'nodes': nodeFailed}
                }
        else:
            resultjson = {"pass": False,
                    "message": "Invalid TopPatch ID %s" % (tpid)
                    }
        return(resultjson)


    def get_by_type(self, pstatus, nodeid=None):
        """
           retrieve package by package status
           pstatus == installed|available|failed|pending
        """
        data = []
        resultjson = {}
        if pstatus == 'available':
            if nodeid:
                count = self.session.query(PackagePerNode).\
                        group_by(PackagePerNode.toppatch_id).\
                        filter(PackagePerNode.installed == False,
                            PackagePerNode.node_id == nodeid,
                            PackagePerNode.pending == False).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False,\
                        PackagePerNode.node_id == nodeid).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            else:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == False,
                        PackagePerNode.pending == False).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            for node_pkg in node_packages:
                avail, installed, pending, failed = \
                        self._get_counts_by_tpid(node_pkg[0])
                pkg1 = self.session.query(Package).\
                        filter(Package.toppatch_id ==\
                        node_pkg[0].toppatch_id).first()
                if pkg1:
                    result = self._json_results(node_pkg[0].vendor_id,
                            node_pkg[0].toppatch_id, node_pkg[0].date_pub,\
                            node_pkg[0].name, node_pkg[0].description,\
                            node_pkg[0].severity, avail,\
                            installed, pending, failed,
                            node_pkg[1].date_installed)
                    data.append(result)
            resultjson = {"count": count, "data": data}

        elif pstatus == 'installed':
            if nodeid:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == True,\
                        PackagePerNode.node_id == nodeid).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == True,\
                        PackagePerNode.node_id == nodeid).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            else:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == True).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == True).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(PackagePerNode).\
                    limit(self.qcount).offset(self.qoffset).all()
            for node_pkg in node_packages:
                avail, installed, pending, failed = \
                        self._get_counts_by_tpid(node_pkg[0])
                pkg1 = self.session.query(Package).\
                        filter(Package.toppatch_id ==\
                        node_pkg[0].toppatch_id).first()
                if pkg1:
                    result = self._json_results(node_pkg[0].vendor_id,
                            node_pkg[0].toppatch_id, node_pkg[0].date_pub,\
                            node_pkg[0].name, node_pkg[0].description,\
                            node_pkg[0].severity, avail,\
                            installed, pending, failed,
                            node_pkg[1].date_installed)
                    data.append(result)
            resultjson = {"count": count, "data": data}

        elif pstatus == 'pending':
            if nodeid:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.node_id == nodeid,\
                        PackagePerNode.pending == True).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == True,\
                        PackagePerNode.node_id == nodeid).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            else:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == False,\
                    PackagePerNode.pending == True).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == True).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            for node_pkg in node_packages:
                avail, installed, pending, failed = \
                        self._get_counts_by_tpid(node_pkg[0])
                pkg1 = self.session.query(Package).\
                        filter(Package.toppatch_id ==\
                        node_pkg[0].toppatch_id).first()
                if pkg1:
                    result = self._json_results(node_pkg[0].vendor_id,
                            node_pkg[0].toppatch_id, node_pkg[0].date_pub,\
                            node_pkg[0].name, node_pkg[0].description,\
                            node_pkg[0].severity, avail,\
                            installed, pending, failed,
                            node_pkg[1].date_installed)
                    data.append(result)
            resultjson = {"count": count, "data": data}

        elif pstatus == 'failed':
            if nodeid:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False,
                        PackagePerNode.node_id == nodeid,
                        PackagePerNode.attempts > 0).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False,\
                        PackagePerNode.node_id == nodeid,\
                        PackagePerNode.attempts > 0).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            else:
                count = self.session.query(PackagePerNode).\
                    group_by(PackagePerNode.toppatch_id).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False,
                        PackagePerNode.attempts > 0).count()
                node_packages = self.session.query(Package, PackagePerNode).\
                    filter(PackagePerNode.installed == False,\
                        PackagePerNode.pending == False,\
                        PackagePerNode.attempts > 0).\
                        group_by(PackagePerNode.toppatch_id).\
                        join(PackagePerNode).\
                        limit(self.qcount).offset(self.qoffset).all()
            for node_pkg in node_packages:
                avail, installed, pending, failed = \
                        self._get_counts_by_tpid(node_pkg[0])
                pkg1 = self.session.query(Package).\
                        filter(Package.toppatch_id ==\
                        node_pkg[0].toppatch_id).first()
                if pkg1:
                    result = self._json_results(node_pkg[0].vendor_id,
                            node_pkg[0].toppatch_id, node_pkg[0].date_pub,\
                            node_pkg[0].name, node_pkg[0].description,\
                            node_pkg[0].severity, avail,\
                            installed, pending, failed,
                            node_pkg[1].date_installed)
                    data.append(result)
            resultjson = {"count": count, "data": data}
        else:
            resultjson = {"pass": False,
                    "message": "Invalid Package Status %s" % (pstatus)
                    }
        return(resultjson)


    def get_by_severity(self, psev, nodeid=None, installed=False):
        """
           retrieve package by package severity
           psev == Critical|Recommended|Optional
        """
        data = []
        resultjson = {}
        if nodeid:
            count = self.session.query(Package, PackagePerNode).\
                filter(Package.severity == psev,
                    PackagePerNode.installed == installed,\
                    PackagePerNode.node_id == nodeid).\
                group_by(PackagePerNode.toppatch_id).\
                join(PackagePerNode).count()
            node_packages = self.session.query(Package, PackagePerNode).\
                filter(Package.severity == psev,
                    PackagePerNode.installed == installed,\
                    PackagePerNode.node_id == nodeid).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(PackagePerNode).limit(self.qcount).\
                    offset(self.qoffset).all()
        else:
            count = self.session.query(Package, PackagePerNode).\
                filter(Package.severity == psev,
                    PackagePerNode.installed == installed).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(PackagePerNode).count()
            node_packages = self.session.query(Package, PackagePerNode).\
                filter(Package.severity == psev,
                    PackagePerNode.installed == installed).\
                    group_by(PackagePerNode.toppatch_id).\
                    join(PackagePerNode).limit(self.qcount).\
                    offset(self.qoffset).all()
        for node_pkg in node_packages:
            avail, installed, pending, failed = \
                    self._get_counts_by_tpid(node_pkg[0])
            pkg1 = self.session.query(Package).\
                    filter(Package.toppatch_id ==\
                    node_pkg[0].toppatch_id).first()
            if pkg1:
                result = self._json_results(node_pkg[0].vendor_id,
                        node_pkg[0].toppatch_id, node_pkg[0].date_pub,\
                        node_pkg[0].name, node_pkg[0].description,\
                        node_pkg[0].severity, avail,\
                        installed, pending, failed,\
                        node_pkg[1].date_installed)
                data.append(result)
        resultjson = {"count": count, "data": data}
        return(resultjson)


    def get_pkg_default(self, nodeid=None):
        """
           retrieve all packages
        """
        count = self.session.query(Package.toppatch_id).count()
        data = []
        for pkg in self.session.query(Package).\
                order_by(Package.date_pub).\
                limit(self.qcount).offset(self.qoffset):
            nodeAvailable = []
            nodeInstalled = []
            nodePending = []
            nodeFailed = []
            countAvailable = 0
            countInstalled = 0
            countFailed = 0
            countPending = 0
            if nodeid:
                node_packages = self.session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id, 
                            PackagePerNode.node_id == nodeid).all()
            else:
                node_packages = self.session.query(PackagePerNode).\
                    filter(PackagePerNode.toppatch_id == pkg.toppatch_id).all()
            for node_pkg in node_packages:
                if node_pkg.installed:
                    countInstalled += 1
                    nodeInstalled.append(node_pkg.node_id)
                elif node_pkg.pending:
                    countPending += 1
                    nodePending.append(node_pkg.node_id)
                elif node_pkg.attempts > 0:
                    countFailed += 1
                    nodeFailed.append(node_pkg.node_id)
                    countAvailable += 1
                    nodeAvailable.append(node_pkg.node_id)
                else:
                    countAvailable += 1
                    nodeAvailable.append(node_pkg.node_id)
                result = self._json_results(pkg.vendor_id, pkg.toppatch_id,
                        pkg.date_pub, pkg.name, pkg.description, pkg.severity,
                        countAvailable, countInstalled, countPending,
                        countFailed, node_pkg.date_installed)
                data.append(result)

        resultjson = {"count": count, "data": data}
        return(resultjson)


    def _get_counts_by_tpid(self, node_pkg, nodeid=None):
        if nodeid:
            available = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.\
                  installed == False, PackagePerNode.pending == \
                  False, PackagePerNode.node_id == nodeid).count()
            installed = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  True, PackagePerNode.node_id == nodeid).count()
            pending = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  False, PackagePerNode.pending == True,\
                  PackagePerNode.node_id == nodeid).count()
            failed = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  False, PackagePerNode.pending == False, \
                  PackagePerNode.node_id == nodeid,\
                  PackagePerNode.attempts > 0).count()
        else:
            available = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.\
                  installed == False, PackagePerNode.pending == \
                  False).count()
            installed = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  True).count()
            pending = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  False, PackagePerNode.pending == True).count()
            failed = self.session.query(PackagePerNode).\
                  filter(PackagePerNode.toppatch_id == \
                  node_pkg.toppatch_id, PackagePerNode.installed == \
                  False, PackagePerNode.pending == False, \
                  PackagePerNode.attempts > 0).count()
        return(available, installed, pending, failed)


    def _json_results(self, vendor, toppatch_id, date_pub, name,
                description, severity, available=0, installed=0,
                pending=0, failed=0, date_installed=None):
        data = {"vendor" :
               {    
                "patchID" : '',         #forcing empty string in patchID
                "name" : vendor
                },   
                "type": "Security Patch",             #forcing Patch into type
                "id": toppatch_id,
                "date" : str(date_pub),
                "date_installed" : str(date_installed),
                "name" : name,
                "description" : description.decode('raw_unicode_escape'),
                "severity" : severity,
                "nodes/need": available,
                "nodes/done": installed,
                "nodes/pend": pending,
                "nodes/fail": failed}
        return data 



