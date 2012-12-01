#!/usr/bin/env python

import re
from db.query_table import get_transactions
from db.client import validate_session
from models.node import *


def retrieve_transactions(session, count=None, offset=None):
    session = validate_session(session)
    transactions, total_count = get_transactions(session, count, offset)
    final_msg = {"count" : total_count, "data" : []}
    for trans in transactions:
        operation_received = None
        key_error = None
        results = None
        node_info = session.query(NodeInfo).filter(NodeInfo.id == trans[1][0].node_id).first()
        if node_info.host_name:
           node = node_info.host_name
        else:
           node = node_info.ip_address
        if trans[1][0].operation_received:
            operation_received = trans[1][0].operation_received.strftime("%m/%d/%Y %H:%M")
        if len(trans[1]) == 1:
            final_msg['data'].append({
                         "operation" : trans[1][0].operation_type,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : node,
                         "results_received" : None,
                         "patch_id" : None,
                         "result" : None,
                         "reboot" : None,
                         "error" : None
                         })
        elif len(trans[1]) == 2:
            final_msg['data'].append({
                         "operation" : trans[1][0].operation_type,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : node,
                         "results_received" : trans[1][0].results_received.strftime("%m/%d/%Y %H:%M"),
                         "patch_id" : trans[1][1][0].patch_id,
                         "result" : trans[1][1][0].result,
                         "reboot" : trans[1][1][0].reboot,
                         "error" : trans[1][1][0].error,
                         })
    return final_msg

