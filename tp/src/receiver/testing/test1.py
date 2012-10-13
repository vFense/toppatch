import json
from OpenSSL import SSL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.update_table import *
from db.query_table import *
from db.client import *
from tools.common import verifyJsonIsValid
from datetime import datetime

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import SSL4ClientEndpoint


class AgentSender(Protocol):
    def sendMessage(self, msg):
        print msg
        self.transport.write(msg)
        self.transport.loseConnection()
    def connectionLost(self, reason):
        reactor.stop()

class AgentFactory(Factory):
    def buildProtocol(self, addr):
        return AgentSender()


class CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv3_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('/opt/TopPatch/var/lib/ssl/server/keys/server.cert')
        ctx.use_privatekey_file('/opt/TopPatch/var/lib/ssl/server/keys/server.key')
        return ctx

def gotProtocol(p):
    print p
    p.sendMessage('{"foo" : "Hello"}')

point = SSL4ClientEndpoint(reactor, "localhost", 9000, CtxFactory())
d = point.connect(AgentFactory())
d.addCallback(gotProtocol)
reactor.run()
