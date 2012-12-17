

from db.client import *
from db.update_table import *
from user.manager import *


ENGINE = init_engine()
session = create_session(ENGINE)
create_group(session, groupname='ADMIN')
create_group(session, groupname='READ_ONLY')
create_group(session, groupname='API_RO')
create_group(session, groupname='API_RW')

acl_admin = {
        'group_id': '1', 'isadmin': True, 'isglobal': True,
        'install': True, 'uninstall': True, 'reboot': True, 'wol': True, 
        'snapshot_creation': True, 'snapshot_removal':True,
        'snapshot_revert': True, 'tag_creation': True, 'tag_removal':True
        }

acl_ro = {
        'group_id': '3', 'isadmin': False, 'isglobal': True,
        'install': False, 'uninstall': False, 'reboot': False, 'wol': False, 
        'snapshot_creation': False, 'snapshot_removal': False,
        'snapshot_revert': False, 'tag_creation': False, 'tag_removal': False,
        'readonly': True
        }
acl_group_a = acl_modifier(session, 'global_group', 'create', **acl_admin)
print acl_group_a
acl_group_b = acl_modifier(session, 'global_group', 'create', **acl_ro)
print acl_group_b

a = create_user(session, username='admin', password='toppatch', groupname='ADMIN', user_name='initializer')
print a
b = create_user(session, username='monitor', password='toppatch', groupname='API_RO', user_name='initializer')
print b
