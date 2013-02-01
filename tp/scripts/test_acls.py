
from db.client import *
from acl.user.auth_tools import *


Engine = init_engine()
session = create_session(Engine)

#a = VerifyUser(session, 'admin')
#print a.run()
#a = VerifyUser(session, 'install')
#print a.run()
#a = VerifyUser(session, 'install', action='allow_install')
#print a.run()
a = VerifyUser(session, 'limited', action='allow_read')
print a.verify()
a = VerifyUser(session, 'limited', action='allow_reboot', node_id=1)
print a.verify()

print a.global_acls

#b = session.query(GlobalGroupAccess).all()
#for i in b:
#    print i.group_id, i.allow_read, i.allow_install, i.is_global, i.deny_all
