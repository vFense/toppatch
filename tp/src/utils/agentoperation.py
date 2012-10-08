#!/usr/bin/env python
from datetime import datetime
from jsonpickle import encode
from utils.sslasync import *
from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import *
import gevent

INSTALL = 'install'
UNINSTALL = 'uninstall'
HIDE = 'hide'
SHOW = 'show'
REBOOT = 'reboot'

class AgentOperation():
    def __init__(self, session, node_list):
        """
        This class will take a list and iterate through it.
        Through each iteration, the object in each array will
        be verified that it was sent as a valid Json object.
        Once each object hsa been verified, it will then update
        the operations table and make a secure socket call to the
        remote agent. Through the use of Gevent, we have made this 
        operation much quicker as well as much safer.
        """
        if type(node_list) == list:
            self.session = session
            self.node_list = node_list
            self.results = []
            self.total_nodes = len(self.node_list)
            self.threads = []
            self._parse_and_pass()
        else:
            raise("You must pass an array")

    def _parse_and_pass(self):
        for node in self.node_list:
            json_valid, jsonobject = verifyJsonIsValid(node)
            if json_valid:
                node_id = jsonobject['node_id']
                exists, node_ip = nodeExists(self.session, node_id=node_id)
                message = None
                if INSTALL in jsonobject:
                    oper_type = INSTALL
                    patch_list = jsonobject[INSTALL]
                    oper_id = self.create_new_operation(node_id, oper_type)
                    message = gevent.spawn(self.create_sof_operation, node_id, \
                        node_ip.ip_address, oper_type, oper_id, patch_list
                        )
                    self.threads.append(message)
                if UNINSTALL in jsonobject:
                    oper_type = UNINSTALL
                    patch_list = jsonobject[UNINSTALL]
                    oper_id = self.create_new_operation(node_id, oper_type)
                    message = gevent.spawn(self.create_sof_operation, node_id, \
                        node_ip.ip_address, oper_type, oper_id, patch_list
                        )
                    self.threads.append(message)
                if HIDE in jsonobject:
                    oper_type = HIDE
                    patch_list = jsonobject[HIDE]
                    oper_id = self.create_new_operation(node_id, oper_type)
                    message = gevent.spawn(self.create_sof_operation, node_id, \
                        node_ip.ip_address, oper_type, oper_id, patch_list
                        )
                    self.threads.append(message)
                if SHOW in jsonobject:
                    oper_type = SHOW
                    patch_list = jsonobject[SHOW]
                    oper_id = self.create_new_operation(node_id, oper_type)
                    message = gevent.spawn(self.create_sof_operation, node_id, \
                        node_ip.ip_address, oper_type, oper_id, patch_list
                        )
                    self.threads.append(message)
                if REBOOT in jsonobject:
                    oper_type = REBOOT
                    oper_id = self.create_new_operation(node_id, oper_type)
                    message = gevent.spawn(self.create_sof_operation, \
                        node_id, node_ip.ip_address, \
                        oper_type, oper_id
                        )
                    self.threads.append(message)
                #else:
                #    raise("Invalid Operation Type %s" % (jsonobject))
            #else:
            #    raise("Invalid JsonObject")

        gevent.joinall(self.threads)
        for job in self.threads:
            self.results.append(job.value)
        #print self.results
        
    def create_sof_operation(self, node_id, node_ip, oper_type, \
            oper_id, patch_list=None):
        """
        Build a valid Json object and than encode it. Once the 
        encoding is complete, we will than pass this message to
        the SSlConnect class.
        """
        jsonobject = None
        if patch_list == None:
            jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id
                     }
        else:
            jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id,
                        "updates" : patch_list
                     }
        msg = encode(jsonobject) 
        connect = SslConnect(node_ip, msg)
        if not connect.error:
            updateOperationRow(self.session, oper_id, oper_recv=True)
        return(node_id, oper_id, connect.read_data, connect.error)


    def create_new_operation(self, node_id, oper_type):
        """
        Add a new operation to the operations table and
        return the autogenerated operation_id
        """
        addOperation(self.session, node_id, oper_type,
                    operation_sent=datetime.now()
                    )
        getoperation, operation = operationExists(self.session,
                    node_id
                    )
        return str(getoperation.id)
