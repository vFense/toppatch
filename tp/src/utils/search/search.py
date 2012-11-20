#!/usr/bin/env python

from models.linux import *
from models.node import *
from models.windows import *
from utils.common import *
from utils.db.client import validateSession




def searchPackages(session, query, column, is_installed=None, all=False):
    session = validateSession
    all_packages []
    if is_installed:
        session.query(AllPackages).
