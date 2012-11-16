#!/usr/bin/env python
from datetime import datetime
from jsonpickle import encode
import logging
from utils.tcpasync import *
from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import *
import gevent

OPERATION = 'operation'
INSTALL = 'install'
UNINSTALL = 'uninstall'
HIDE = 'hide'
SHOW = 'show'
REBOOT = 'reboot'
UPDATESINSTALLED = 'updates_installed'
UPDATESPENDING = 'updates_pending'
SYSTEMINFO = 'system_info'
SYSTEMAPPLICATIONS = 'system_applications'
DATA = 'data'
SCHEDULE = 'schedule'
TIME = 'time'

class AgentOperation():
    def __init__(self, node_list):
    #def __init__(self, session, node_list):
        """
        This class will take a list and iterate through it.
        Through each iteration, the object in each array will
        be verified that it was sent as a valid Json object.
        Once each object hsa been verified, it will then update
        the operations table and make a secure socket call to the
        remote agent. Through the use of Gevent, we have made this 
        operation much quicker as well as much safer.
        """
        ENGINE = initEngine()
        self.session = createSession(ENGINE)
        self.node_list = node_list
        self.total_nodes = None
        self.results = {}
        self.json_out = {}
        if type(node_list) == list:
            self.node_list = node_list
            self.total_nodes = len(self.node_list)
        else:
            json_valid, self.node_list = verifyJsonIsValid(node_list)
            if type(self.node_list) != list:
                self.node_list = [self.node_list]

    def run(self):
        self.results = []
        self.threads = []
        for node in self.node_list:
            if type(node) != dict:
                json_valid, jsonobject = verifyJsonIsValid(node)
            else:
                json_valid = True
                jsonobject = node
            if json_valid:
                node_id = jsonobject['node_id']
                self.node_exists, node = nodeExists(self.session, node_id=node_id)
                print self.node_exists, node, jsonobject
                oper_type = jsonobject[OPERATION]
                print oper_type
                oper_id = self.create_new_operation(node_id, oper_type)
                time_block_exists, time_block, self.json_out = timeBlockExistsToday(self.session, start_date=datetime.today().date(), start_time=datetime.now().time())
                if time_block_exists:
                    return self.json_out
                if not DATA in jsonobject:
                    message = gevent.spawn(self.create_sof_operation, node_id, 
                        node.ip_address, oper_type, oper_id
                        )
                    self.threads.append(message)
                elif DATA in jsonobject:
                    if type(jsonobject[DATA]) == list:
                        data = jsonobject[DATA]
                        message = gevent.spawn(self.create_sof_operation, node_id, 
                                node.ip_address, oper_type, oper_id, data
                                )
                        self.threads.append(message)
                    else:
                        raise("You must pass an array")
        gevent.joinall(self.threads, 0.5)
        print "Starting Thread"
        for job in self.threads:
            self.results.append(job.value)
        print self.results
        self.session.close
        
    def create_sof_operation(self, node_id, node_ip, oper_type, \
            oper_id, data_list=None):
        """
        Build a valid Json object and than encode it. Once the 
        encoding is complete, we will than pass this message to
        the TcpConnect class.
        """
        jsonobject = None
        if data_list == None:
            jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id
                     }
        else:
            jsonobject = {
                        "operation" : oper_type,
                        "operation_id" : oper_id,
                        "data" : data_list
                     }
        updateNodeStats(self.session, node_id)
        updateNetworkStats(self.session)
        msg = encode(jsonobject) 
        msg = msg + '<EOF>'
        print msg
        response = None
        connect = TcpConnect(node_ip, msg)
        completed = False
        if not connect.error and connect.read_data:
            response = verifyJsonIsValid(connect.read_data)
            print response
            if response[1]['operation'] == 'received':
                completed = True
                updateOperationRow(self.session, oper_id, oper_recv=True)
                updateNodeStats(self.session, node_id)
                updateNetworkStats(self.session)
                if oper_type == 'reboot':
                    updateRebootStatus(self.session, node_id, oper_type)
                if 'data' in jsonobject:
                    for patch in jsonobject['data']:
                        if oper_type == 'install':
                            patcher = self.session.query(ManagedWindowsUpdate).filter_by(toppatch_id=patch).filter_by(node_id=node_id)
                            patcher.update({"pending" : True})
                            self.session.commit()
                            updateNodeStats(self.session, node_id)
                            updateNetworkStats(self.session)
            self.result ={
                          "node_id" : node_id,
                          "operation_id" : oper_id,
                          "message" : connect.read_data,
                          "error" : connect.error,
                          "pass" : completed
                          }
        return self.result


    def create_new_operation(self, node_id, oper_type):
        """
        Add a new operation to the operations table and
        return the autogenerated operation_id
        """
        oper = addOperation(self.session, node_id, oper_type,
                    operation_sent=datetime.now()
                    )
        return oper.id
