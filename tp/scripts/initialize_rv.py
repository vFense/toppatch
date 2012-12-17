

from db.client import *
from db.update_table import *
from user.manager import *


ENGINE = init_engine()
session = create_session(ENGINE)
#create_group(session, groupname='ADMIN')
#create_group(session, groupname='READ_ONLY')
#create_group(session, groupname='API_RO')
#create_group(session, groupname='API_RW')

acl_admin = {
        'group_id': '1', 'isadmin': 'true', 'isglobal': 'true',
        'install': 'true', 'uninstall': 'true', 'reboot': 'true', 'wol': 'true', 
        'snapshot_creation': 'true', 'snapshot_removal':'true',
        'snapshot_revert': 'true', 'tag_creation': 'true', 'tag_removal':'true'
        }

acl_ro = {
        'group_id': '3', 'isadmin': 'false', 'isglobal': 'true',
        'install': 'false', 'uninstall': 'false', 'reboot': 'false', 'wol': 'false', 
        'snapshot_creation': 'false', 'snapshot_removal': 'false',
        'snapshot_revert': 'false', 'tag_creation': 'false', 'tag_removal': 'false',
        'readonly': 'true'
        }
acl_group_a = acl_modifier(session, 'global_group', 'create', acl_admin)
print acl_group_a
acl_group_b = acl_modifier(session, 'global_group', 'create', acl_ro)
print acl_group_b

a = create_user(session, username='admin', password='toppatch', groupname='ADMIN', user_name='initializer')
print a
b = create_user(session, username='monitor', password='toppatch', groupname='API_RO', user_name='initializer')
print b
