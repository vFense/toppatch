#!/usr/bin/env python
from datetime import datetime
from twisted.internet import reactor, defer
from sslStart import SslConnector
#SslConnector('127.0.0.1', '{"operation" : "updates_pending", "operation_id" : "1"}')
class AgentOperation():
    def __init__(self, session, node_list):
        if type(node_list) == list:
            self.session = session
            self.node_list = node_list
            self.results = []
            self.total_nodes = len(self.node_list)
        for node in self.node_list:
            json_valid = verifyJsonIsValid(node)
            if json_valid[0]:
                jsonobject = json_valid[1]
                node_id = jsonobject['node_id']
                if jsonobject.has_key('install'):
                    oper_type = 'install'
                    patch_list = jsonobject['install']
                    oper_id = add_oper_get_oper(node_id, oper_type)
                    results = self.install(node_id, oper_type, 
                            oper_id, patch_list
                            )
        
    def install(self, node_id, oper_type, oper_id):
        jsonobject = {
                        "operation" : operation,
                        "operation_id" : oper_id,
                        "updates" : node["install"]
                     }


    def add_oper_get_oper(self, node_id, oper_type):
        addOperation(self.session, nodeId, oper_type,
                    operation_sent=datetime.now()
                    )
        getoperation = operationExists(self.session,
                    'nodeId'
                    )
        if getoperation.node_id == node_id:
            return get_operation.id


