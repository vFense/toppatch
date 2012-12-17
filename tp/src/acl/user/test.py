from db.client import *
from db.update_table import *
from acl.user.auth_tools import *

ENGINE = init_engine()
session = create_session(ENGINE)

a = VerifyUser(session, user_name='dinesh11', action='allow_install', tag_name='Apache')
b = a.run()
print b
#c = VerifyUser(session, user_name='test', action='allow_install', node_id=1)
#d = c.run()
#print d
e = VerifyUser(session, user_name='demo2', action='allow_install', node_id=1)
f = e.run()
print f
