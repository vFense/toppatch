
from receiver.sslStart import SslConnector
#from twisted.internet import reactor, defer

#a = defer.Deferred()
#reactor.callLater(1, a.callback, SslConnector("127.0.0.1", '{"operation" : "updates_pending", "operation_id" : "1"}'))
#print dir(a)
#print a.msg
a = SslConnector('127.0.0.1', '{"operation" : "updates_pending", "operation_id" : "1"}')
print dir(a)
