from utils.db.nupdate_table import *
from utils.db.nquery_table import *
from utils.db.client import *
from utils.common import *
from utils.nagentoperation import *
#from sslconnect import SslConnect
from utils.sslasync import SslConnect

#o = 20 
engine = initEngine()
session = createSession(engine)
node_list = ['{"node_id" : 1, "operation" :"install", "data" : ["2014", "2012", "2013"]}','{"node_id" : 1, "operation" : "show", "data" : ["2014", "2012", "2013"]}', '{"node_id" : 1, "operation" : "uninstall", "data" : ["2014", "2012", "2013"]}','{"node_id" : 1, "operation" : "hide", "data" : ["2014", "2012", "2013"]}', '{"node_id" : 1, "operation" : "reboot"}']
#node_list = ['{"node_id" : 1, "operation_id" : 1, "operation" : "reboot"}']
#updateNode(session,"1")
#print nodeExists(session, node_id="1")
#print dir(updateNode)
#node_list = '{"node_id" : "1", "operation" : "status"}'

#for i in range(o):
#    print i
#    AgentOperation(session,node_list)
AgentOperation(session,node_list)
#SslConnect("127.0.0.1",node_list)
