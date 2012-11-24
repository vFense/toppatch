from db.update_table import *
from db.query_table import *
from db.client import *
from utils.common import *
from networking.agentoperation import *
#from sslconnect import SslConnect
from networking.tcpasync import TcpConnect
from jsonpickle import encode


#To test out csrlistener.py, uncomment the below...
"""
csr = encode({"pem" : "-----BEGIN CERTIFICATE REQUEST-----\nMIICmjCCAYICAQMwVTENMAsGA1UEAxMEdGVzdDEMMAoGA1UEChMDZm9vMQwwCgYD\nVQQLEwNmZWUxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJGTDEOMAwGA1UEBxMFRG9y\nYWwwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDqHsmhkydrTBq5EKyF\nqC4AGQKu9RBdiiT/t4aEUjj2D8/VDfmoyc3N0mtyhRwge25YFLIMVHhTY16GV8rl\nXyoAHc7/n5ZW34GyLKEXqAbPgufYAEvJQsg8DVud9AqAe2TA4JlTU14dfvzStH0U\nG8J7ayXfEYhce4Qw92Cywi8FoEwSzPd3lPKECk4RJBmMKUtL3MP2Omc4AU9NN01D\nK56cxyJ+Q9I60m8/IV1C8iL/bd96zf8DmvLuC7sH6XakveS/JFRLU0YufM6i0Xtd\nvgTSmvjrz5suHyKBv4RTPGvE6O3CYVzSjGd9oQQgFSshUWR4Yz+hNOGZThh5j0Dj\nrDkBAgMBAAGgADANBgkqhkiG9w0BAQ0FAAOCAQEAuJhT5VC4RLYgcIwtRjymUiHT\npmsFjUzWrVm4dmqrY2jQQ1yg1b7BiF8uMuwsCci0+0YYDMO9fxHYuKEFbMBSQmly\nLc77DmgmTfDjWInrQ4/1SuvSSS/DWo6lNDDEJTraJjQKIj1Xy9ZnDanjMctt5qnb\nXBKFxl2HBnfO0kyK1uuMB8DF9ZeCQ48ygr9c6ETHaLEIv8weNDh92+altbx3SGpw\ns5HDyRJxpePox/0LwZYe0oohKuUN8gW7wzywbQqIW/FWQhhE/fpw+8aMRVnIxFzV\nBrzBbEW79Lyhw+a9Yj/eNVvWxYPY3CqowBvKQT2ZoHJWBYphW+H2orciivg9bA==\n-----END CERTIFICATE REQUEST-----\n"})
a = TcpConnect("127.0.0.1", csr, secure=False, port=9002)
print a.read_data
print a.error
print a.connection_count
"""

#To test the sending of operations to the remote agent, use the below.. (With out AgentOperation)
#The node_id is the node_id in the node_info table. Make sure the IP Address actually matches the node_id
"""
node_list = '{"node_id" : "1", "operation" : "system_info", "operation_id" : "22"}'
a = TcpConnect("10.35.55.64", node_list, port=9003)
print a.read_data
print a.error
print a.connection_count
"""

#To test the sending of operations to the remote agent, use the below.. (With AgentOperation)
"""
node_list = '{"node_id" : "1", "operation" : "system_info", "operation_id" : "22"}'
a = AgentOperation(node_list)
a.run()
print a.results
"""

#Or you can do this with a tag_id instead of a node_id.....
"""
tag_list = '{"tag_id" : "9", "operation" : "system_info", "operation_id" : "22"}'
a = AgentOperation(tag_list)
a.run()
print a.results
"""
