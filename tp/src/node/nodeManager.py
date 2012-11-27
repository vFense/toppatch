#!/usr/bin/env python

from db.update_table import *
from utils.common import *


def changeDisplayName(session, nodeid, displayname):
    session = validateSession(session)
    completed, msg, success = \
            modifyDisplayName(session, nodeid, displayname)
    out = {"pass" : success,
           "message" : msg
          }
    return out
    
