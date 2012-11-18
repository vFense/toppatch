#!/usr/bin/env python

from utils.db.query_table import getTransactions
from utils.db.client import validateSession


def retrieveTransactions(session):
    session = validateSession(session)
    transactions = getTransactions(session)
    transaction = []
    for trans in transactions:
        if trans[1][0].operation_received:
            operation_received = operation_received.strftime("%m/%d/%Y %H:%M")
        if len(trans[1]) == 1:
            transaction.append({
                         "operation" : trans[1][0].operation_type,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : trans[1][0].node_id,
                         "results_received" : None,
                         "patch_id" : None,
                         "result" : None,
                         "reboot" : None,
                         "error" : None
                         })
        elif len(trans[1]) == 2:
            transaction.append({
                         "operation" : trans[1][0].operation_type,
                         "operation_sent" : trans[1][0].operation_sent.strftime("%m/%d/%Y %H:%M"),
                         "operations_received" : operation_received,
                         "node_id" : trans[1][0].node_id,
                         "results_received" : trans[1][0].results_received.strftime("%m/%d/%Y %H:%M"),
                         "patch_id" : trans[1][1].patch_id,
                         "result" : trans[1][1].result,
                         "reboot" : trans[1][1].reboot,
                         "error" : trans[1][1].error
                         })
    return transaction

