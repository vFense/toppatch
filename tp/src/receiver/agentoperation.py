#!/usr/bin/env python
from datetime import datetime
from jsonpickle import encode
from twisted.internet import reactor, defer
from sslconnect import *
from db.update_table import *
from db.query_table import *
from db.client import *
from tools.common import *


INSTALL = 'install'
UNINSTALL = 'uninstall'
HIDE = 'hide'
SHOW = 'show'
class AgentOperation():
    def __init__(self, session, node_list):
        if type(node_list) == list:
            self.session = session
            self.node_list = node_list
            self.results = []
            self.total_nodes = len(self.node_list)
        for node in self.node_list:
            json_valid, jsonobject = verifyJsonIsValid(node)
            if json_valid:
                node_id = jsonobject['node_id']
                node_ip = nodeExists(self.session, node_id=node_id)
                if INSTALL in jsonobject:
                    oper_type = INSTALL
                    patch_list = jsonobject[INSTALL]
                if UNINSTALL in jsonobject:
                    oper_type = UNINSTALL
                    patch_list = jsonobject[UNINSTALL]
                if HIDE in jsonobject:
                    oper_type = HIDE
                    patch_list = jsonobject[HIDE]
                if SHOW in jsonobject:
                    oper_type = SHOW
                    patch_list = jsonobject[SHOW]
                oper_id = self.create_new_operation(node_id, oper_type)
                message = self.create_sof_operation(node_ip.ip_address,
                        oper_type, oper_id, patch_list
                        )
                self.results.append((node_id, oper_id, message.read_data))
                print self.results
            else:
                print "Invalid Json"
        
    def create_sof_operation(self, node_ip, oper_type, oper_id, patch_list):
        jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id,
                        "updates" : patch_list
                     }
        msg = encode(jsonobject) 
        connect = SslConnect(node_ip, msg)
        if not connect.connection_error or connect.write_error \
                or connect.read_error:
            updateOperationRow(self.session, oper_id, oper_recv=True)
        return connect


    def create_new_operation(self, node_id, oper_type):
        addOperation(self.session, node_id, oper_type,
                    operation_sent=datetime.now()
                    )
        getoperation, operation = operationExists(self.session,
                    node_id
                    )
        return str(getoperation.id)

