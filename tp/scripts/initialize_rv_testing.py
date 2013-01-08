import os
import shutil
import sys
import re
from time import sleep
import subprocess
import logging, logging.config
from db.client import *
from user.manager import *

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')
MYSQL_PATH = '/opt/TopPatch/mysql/current'
PYTHON_PATH = '/opt/TopPatch/python/current'
acl_admin = {
        'group_id': '1', 'is_admin': 'true', 'is_global': 'true',
        'allow_install': 'true', 'allow_uninstall': 'true',
        'allow_reboot': 'true', 'allow_wol': 'true', 
        'allow_snapshot_creation': 'true', 'allow_snapshot_removal':'true',
        'allow_snapshot_revert': 'true', 'allow_tag_creation': 'true',
        'allow_tag_removal':'true', 'allow_read': 'true'
        }

acl_ro2 = {
        'group_id': '2', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'false', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }


acl_ro3 = {
        'group_id': '3', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'false', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }

acl_ro6 = {
        'user_id': '6', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'true', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }


acl_ri5 = {
        'user_id': '5', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'true', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }


acl_ni5 = {
        'user_id': '5', 'node_id': '1',
        'allow_install': 'true', 'allow_uninstall': 'true',
        'allow_reboot': 'true', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }


acl_api_rw = {
        'group_id': '4', 'is_admin': 'true', 'is_global': 'true',
        'allow_install': 'true', 'allow_uninstall': 'true',
        'allow_reboot': 'true', 'allow_wol': 'true', 
        'allow_snapshot_creation': 'true', 'allow_snapshot_removal':'true',
        'allow_snapshot_revert': 'true', 'allow_tag_creation': 'true',
        'allow_tag_removal':'true', 'allow_read': 'true'

        }

acl_deny_all = {
        'group_id': '5', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'false', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'deny_all': 'true', 'allow_read': 'false'
        }

acl_allow_install = {
        'group_id': '6', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'true', 'allow_uninstall': 'false',
        'allow_reboot': 'false', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'allow_read': 'true'
        }

acls1 = [acl_admin, acl_ro2, acl_ro3, acl_api_rw, acl_deny_all, acl_allow_install]
acls2 = [ acl_ro6, acl_ri5]
groups = ['ADMIN', 'READ_ONLY', 'API_RO', 'API_RW', 'DENY_ALL', 'INSTALL_ONLY']
users_to_groups = [
        ('admin', 'ADMIN'),
        ('read_only', 'READ_ONLY'),
        ('monitor', 'API_RO'),
        ('remote', 'API_RW'),
        ('limited', 'DENY_ALL'),
        ('install', 'INSTALL_ONLY'),
        ]

def initialize_db():
    if not os.path.exists('/opt/TopPatch/var/tmp'):
        os.mkdir('/opt/TopPatch/var/tmp')
    if not os.path.exists('/opt/TopPatch/var/log'):
        os.mkdir('/opt/TopPatch/var/log')
    completed = True
    msg = 'RV Database initialized and populated'
    os.chdir(MYSQL_PATH)
    mysql_install = subprocess.Popen(['./scripts/mysql_install_db'],
            stdout=subprocess.PIPE)
    mysql_install.poll()
    mysql_install.wait()
    if mysql_install.returncode == 0:
        mysql_start = subprocess.Popen(['./support-files/mysql.server',
            'start'], stdout=subprocess.PIPE)
        mysql_start.poll()
        mysql_start.wait()
    else:
        completed = False
        msg = 'Failed during MySQL initialization'
        return(completed, msg)
    if mysql_start.returncode == 0:
        mysql_password = subprocess.Popen(['./bin/mysqladmin',
            '-u', 'root', 'password', 'topmiamipatch'],
            stdout=subprocess.PIPE)
        mysql_password.poll()
        mysql_password.wait()
    else:
        completed = False
        msg = 'Failed during MySQL startup process'
        return(completed, msg)
    if mysql_password.returncode == 0:
        create_db = subprocess.Popen(['./bin/mysql',
            '-u', 'root', '--password=topmiamipatch',
            '-e create database toppatch_server;'],
            stdout=subprocess.PIPE)
        create_db.poll()
        create_db.wait()
    else:
        completed = False
        msg = 'Failed during MySQL password change'
        return(completed, msg)
    if create_db.returncode == 0:
        os.chdir(PYTHON_PATH)
        create_tables = subprocess.Popen(['./bin/python',
            '/opt/TopPatch/tp/scripts/create_tables.py'],
            stdout=subprocess.PIPE)
        create_tables.poll()
        create_tables.wait()
    else:
        completed = False
        msg = 'Failed during MySQL toppatch_server db creation'
        return(completed, msg)
    if not create_tables.returncode == 0:
        completed = False
        msg = 'Failed during MySQL toppatch_server tables creation'
        return(completed, msg)
    return(completed, msg)


def group_creation(session):
    completed = True
    for group in groups:
        g = create_group(session, groupname=group)
        if not g['pass']:
            completed = False
    return(completed)


def acl_creation_group(session):
    completed = True
    for acl in acls1:
        acl_group = acl_modifier(session, 'global_group', 'create', acl)
        if not acl_group['pass']:
            completed = False
    return(completed)

def acl_creation_user(session):
    completed = True
    for acl in acls2:
        acl_user = acl_modifier(session, 'global_user', 'create', acl)
        if not acl_user['pass']:
            completed = False
    return(completed)


def user_creation(session):
    completed = True
    for users in users_to_groups:
        user = create_user(session, username=users[0], password='toppatch',
                groupname=users[1], user_name='initializer')
        if not user['pass']:
            completed = False
    return(completed)


def clean_database(connected):
    os.chdir(MYSQL_PATH)
    completed = True
    sql_msg = None
    msg = None
    if connected:
        mysql_stop = subprocess.Popen(['./support-files/mysql.server',
            'stop'], stdout=subprocess.PIPE)
        mysql_stop.poll()
        mysql_stop.wait()
        if mysql_stop.returncode == 0:
            sql_msg = 'MySQL stopped successfully\n'
        else:
            sql_msg = 'MySQL couldnt be stopped\n'
    try:
        a = shutil.rmtree(MYSQL_PATH+'/data')
        msg = 'MySQL Data directory removed and cleaned'
    except Exception as e:
        msg = 'MySQL Data directory could not be removed'
        completed = False
    if sql_msg and msg:
        msg = sql_msg + msg
    elif sql_msg and not msg:
        msg = sql_msg
    return(completed, msg)


if __name__ == '__main__':
    try:
        ENGINE = init_engine()
        ENGINE.connect()
        connected = True
        sql_msg = 'MySQL is Running'
    except Exception as e:
        connected = False
        sql_msg = 'MySQL is not Running'
    print sql_msg
    db_clean, db_msg = clean_database(connected)
    print db_msg
    db_initialized, msg = initialize_db()
    initialized = False
    if db_initialized:
        ENGINE = init_engine()
        session = create_session(ENGINE)
        print 'MySQL is Running and Connected'
        groups_created = group_creation(session)
        if groups_created:
            print 'RV Groups were created successfully'
            group_acls_created = acl_creation_group(session)
            if group_acls_created:
                print 'RV ACLs for the user Groups were created successfully'
                users_created = user_creation(session)
                if users_created:
                    print 'RV default Users were created successfully'
                    user_acls_created = acl_creation_user(session)
                    if user_acls_created:
                        print 'RV ACLs for the users were created successfully'
                        initialized = True
        if initialized:
            print 'RV environment has been succesfully initialized\n%s' %\
                    ('Please login as user=admin, passwd=toppatch')
        else:
            print 'RV Failed to initialize, please contact TopPatch support'
    else:
        print msg
