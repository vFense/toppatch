
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


def return_tag_info_in_json(tagdict, node_info, oper, tag, pos, append=False):
    tagdict[oper].append({})
    tagdict[oper][tag_pos[tag.tag]]['tag'] = tag.tag
    tagdict[oper][tag_pos[tag.tag]]['nodes'] = []
    tagdict[oper][tag_pos[tag.tag]]['nodes'].append(
            return_node_info_in_json(node_info))
    return(tagdict)

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
                            tagdict['done'].append({'tag': tag.tag,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['done'][tag_pos[tag.tag]]['tag']:
                            tagdict['done'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif node.installed and node.pending:
                        if not tag_pos[tag.tag] in range(len(tagdict['pending'])):
                            tagdict['pending'].append({'tag': tag.tag,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['pending'][tag_pos[tag.tag]]['tag']:
                            tagdict['pending'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif not node.installed and node.attempts >=1:
                        if not tag_pos[tag.tag] in range(len(tagdict['failed'])):
                            tagdict['failed'].append({'tag': tag.tag,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['failed'][tag_pos[tag.tag]]['tag']:
                            tagdict['failed'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))
                    elif not node.installed and node.attempts ==0:
                        if not tag_pos[tag.tag] in range(len(tagdict['available'])):
                            tagdict['available'].append({'tag': tag.tag,
                                    'nodes': [return_node_json(node_info)]
                                    })
                        elif tag.tag in tagdict['available'][tag_pos[tag.tag]]['tag']:
                            tagdict['available'][tag_pos[tag.tag]]['nodes'].append(
                                    return_node_json(node_info))

        return(tagdict)
    else:
        tagdict['pass'] = False
        tagdict['message'] = 'Tags do not exist for toppatchid %s' % (tpid)
        return(tagdict)
