

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
        'group_id': '1', 'is_admin': 'true', 'is_global': 'true',
        'allow_install': 'true', 'allow_uninstall': 'true',
        'allow_reboot': 'true', 'allow_wol': 'true', 
        'allow_snapshot_creation': 'true', 'allow_snapshot_removal':'true',
        'allow_snapshot_revert': 'true', 'allow_tag_creation': 'true',
        'allow_tag_removal':'true'
        }

acl_ro = {
        'group_id': '3', 'is_admin': 'false', 'is_global': 'true',
        'allow_install': 'false', 'allow_uninstall': 'false',
        'allow_reboot': 'false', 'allow_wol': 'false', 
        'allow_snapshot_creation': 'false', 'allow_snapshot_removal': 'false',
        'allow_snapshot_revert': 'false', 'allow_tag_creation': 'false',
        'allow_tag_removal': 'false', 'read_only': 'true'
        }

acl_api_rw = {
        'group_id': '4', 'is_admin': 'true', 'is_global': 'true',
        'allow_install': 'true', 'allow_uninstall': 'true',
        'allow_reboot': 'true', 'allow_wol': 'true', 
        'allow_snapshot_creation': 'true', 'allow_snapshot_removal':'true',
        'allow_snapshot_revert': 'true', 'allow_tag_creation': 'true',
        'allow_tag_removal':'true'
        }

acl_group_a = acl_modifier(session, 'global_group', 'create', acl_admin)
print acl_group_a
acl_group_b = acl_modifier(session, 'global_group', 'create', acl_ro)
print acl_group_b
acl_group_c = acl_modifier(session, 'global_group', 'create', acl_api_rw)
print acl_group_c

a = create_user(session, username='admin', password='toppatch', groupname='ADMIN', user_name='initializer')
print a
b = create_user(session, username='monitor', password='toppatch', groupname='API_RO', user_name='initializer')
print b
c = create_user(session, username='remote', password='toppatch', groupname='API_RW', user_name='initializer')
print c
