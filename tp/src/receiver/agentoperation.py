#!/usr/bin/env python
from datetime import datetime
from jsonpickle import encode
from twisted.internet import reactor, defer
from sslStart import SslConnector
from db.update_table import *
from db.query_table import *
from tools.common import *

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
                node_ip = nodeExists(self.session, node_id=node_id)
                
                if jsonobject.has_key('install'):
                    oper_type = 'install'
                    patch_list = jsonobject['install']
                    oper_id = self.add_oper_get_oper(node_id, oper_type)
                    results = self.install(node_ip.ip_address,
                            oper_type, oper_id, patch_list
                            )
                    self.results.append((node_id, oper_id, results))
                    print self.results
        
    def install(self, node_ip, oper_type, oper_id, patch_list):
        jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id,
                        "updates" : patch_list
                     }
        msg = encode(jsonobject) 
        print msg
        connect = SslConnector(node_ip, msg)
        return connect.results


    def add_oper_get_oper(self, node_id, oper_type):
        addOperation(self.session, node_id, oper_type,
                    operation_sent=datetime.now()
                    )
        getoperation, operation = operationExists(self.session,
                    node_id
                    )
        return str(getoperation.id)



#node_list = ['{"node_id" : "1", "install" : ["2014", "2012", "2013"]}']
#engine = initEngine()
#session = createSession(engine)
#AgentOperation(session, node_list)
