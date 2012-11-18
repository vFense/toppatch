from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import *
from utils.agentoperation import *
#from sslconnect import SslConnect
from utils.tcpasync import TcpConnect
from jsonpickle import encode

o = 20 
engine = initEngine()
session = createSession(engine)
#node_list = ['{"node_id" : 1, "install" : ["2014", "2012", "2013"]}','{"node_id" : 1, "show" : ["2014", "2012", "2013"]}', '{"node_id" : 1, "uninstall" : ["2014", "2012", "2013"]}','{"node_id" : 1, "hide" : ["2014", "2012", "2013"]}', '{"node_id" : 1, "operation_id" : 1, "operation" : "reboot"}']
csr = encode({"pem" : "-----BEGIN CERTIFICATE REQUEST-----\nMIICmjCCAYICAQMwVTENMAsGA1UEAxMEdGVzdDEMMAoGA1UEChMDZm9vMQwwCgYD\nVQQLEwNmZWUxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJGTDEOMAwGA1UEBxMFRG9y\nYWwwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDqHsmhkydrTBq5EKyF\nqC4AGQKu9RBdiiT/t4aEUjj2D8/VDfmoyc3N0mtyhRwge25YFLIMVHhTY16GV8rl\nXyoAHc7/n5ZW34GyLKEXqAbPgufYAEvJQsg8DVud9AqAe2TA4JlTU14dfvzStH0U\nG8J7ayXfEYhce4Qw92Cywi8FoEwSzPd3lPKECk4RJBmMKUtL3MP2Omc4AU9NN01D\nK56cxyJ+Q9I60m8/IV1C8iL/bd96zf8DmvLuC7sH6XakveS/JFRLU0YufM6i0Xtd\nvgTSmvjrz5suHyKBv4RTPGvE6O3CYVzSjGd9oQQgFSshUWR4Yz+hNOGZThh5j0Dj\nrDkBAgMBAAGgADANBgkqhkiG9w0BAQ0FAAOCAQEAuJhT5VC4RLYgcIwtRjymUiHT\npmsFjUzWrVm4dmqrY2jQQ1yg1b7BiF8uMuwsCci0+0YYDMO9fxHYuKEFbMBSQmly\nLc77DmgmTfDjWInrQ4/1SuvSSS/DWo6lNDDEJTraJjQKIj1Xy9ZnDanjMctt5qnb\nXBKFxl2HBnfO0kyK1uuMB8DF9ZeCQ48ygr9c6ETHaLEIv8weNDh92+altbx3SGpw\ns5HDyRJxpePox/0LwZYe0oohKuUN8gW7wzywbQqIW/FWQhhE/fpw+8aMRVnIxFzV\nBrzBbEW79Lyhw+a9Yj/eNVvWxYPY3CqowBvKQT2ZoHJWBYphW+H2orciivg9bA==\n-----END CERTIFICATE REQUEST-----\n"})
#node_list = ['{"node_id" : 1, "operation_id" : 1, "operation" : "reboot"}']
#updateNode(session,"1")
#print nodeExists(session, node_id="1")
#print dir(updateNode)
node_list = '{"node_id" : "1", "operation" : "system_info", "operation_id" : "22"}'

#for i in range(o):
#    print i
#    AgentOperation(session,node_list)
a = AgentOperation(node_list)
a.run()
#TcpConnect("127.0.0.1",csr, secure=False)
#a = TcpConnect("127.0.0.1", csr, secure=False, port=9002)
#a = TcpConnect("10.0.0.1", csr, secure=False, port=9005)
#a = TcpConnect("10.35.55.64", node_list, port=9003)
print a.read_data
print a.error
print a.connection_count
