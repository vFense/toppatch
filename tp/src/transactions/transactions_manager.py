#!/usr/bin/env python

import re
from db.query_table import get_transactions
from db.client import validate_session
from models.node import *
from models.virtualization import *


def retrieve_transactions(session, count=None, offset=None):
    """
        Return a list of historical transactions of the RV system in json
    """
    session = validate_session(session)
    transactions, total_count = get_transactions(session, count, offset)
    final_msg = {"count" : total_count, "data" : []}
    for trans in transactions:
        operation_received = None
        key_error = None
        results = None
        node = None
        node_info = session.query(NodeInfo).filter(NodeInfo.id == trans[1][0].node_id).first()
        if node_info.is_vm:
            vm = session.query(VirtualMachineInfo).\
                filter(VirtualMachineInfo.node_id == \
                node_info.id).first()
            if vm:
                vm_name = vm.vm_name
        else:
            vm_name = None
        if trans[1][0].operation_received:
            operation_received = trans[1][0].operation_received.strftime("%m/%d/%Y %H:%M")
        print trans
        if len(trans[1]) == 1:
            final_msg['data'].append({
                         "operation" : trans[1][0].operation_type,
                         "username" : trans[1][0].username,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : node_info.id,
                         "node_host_name" : node_info.host_name,
                         "node_display_name" : node_info.display_name,
                         "node_vm_name" : vm_name,
                         "node_ip_address" : node_info.ip_address,
                         "node_computer_name" : node_info.computer_name,
                         "results_received" : None,
                         #"patch_id" : None,
                         #"succeeded" : None,
                         #"reboot" : None,
                         "error" : None
                         })
        elif len(trans[1]) >= 2:
            final_msg['data'].append({
                         "operation" : trans[1][0].operation_type,
                         "username" : trans[1][0].username,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : node_info.id,
                         "node_host_name" : node_info.host_name,
                         "node_display_name" : node_info.display_name,
                         "node_vm_name" : vm_name,
                         "node_ip_address" : node_info.ip_address,
                         "node_computer_name" : node_info.computer_name,
                         "results_received" : trans[1][1].results_received.strftime("%m/%d/%Y %H:%M"),
                         #"patch_id" : trans[1][1].patch_id,
                         "result" : trans[1][1].succeeded,
                         #"reboot" : trans[1][1].reboot,
                         "error" : trans[1][1].error,
                         })
    return final_msg

