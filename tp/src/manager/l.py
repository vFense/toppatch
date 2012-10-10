from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Chat(LineReceiver):
    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"
    def connectionMade(self):
        self.sendLine("What's your name?")
    def connectionLost(self, reason):
        if self.users.has_key(self.name):
            del self.users[self.name]
    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)
    def handle_GETNAME(self, name):
        if self.users.has_key(name):
            self.sendLine("Name taken, please choose another.")
            return
        self.sendLine("Welcome, %s!" % (name,))
        self.name = name
        self.users[name] = self
        self.state = "CHAT"
    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)

class ChatFactory(Factory):
    def __init__(self):
        self.users = {} # maps user names to Chat instances
    def buildProtocol(self, addr):
        return Chat(self.users)

myContextFactory = ssl.DefaultOpenSSLContextFactory(
    '/opt/TopPatch/var/lib/ssl/server/keys/server.key','/opt/TopPatch/var/lib/ssl/server/keys/server_ca.cert', SSL.SSLv3_METHOD
    )

ctx = myContextFactory.getContext()
#ctx = SSL.Context(SSL.SSLv3_METHOD)
ctx.set_cipher_list('TLSv1+HIGH:!SSLv2:RC4+MEDIUM:!aNULL:!eNULL:!3DES:@STRENGTH')

ctx.set_verify(
    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
    verifyCallback
    )

# Since we have self-signed certs we have to explicitly
# tell the server to trust them.
ctx.load_verify_locations("/opt/TopPatch/var/lib/ssl/server/keys/server_ca.cert")

reactor.listenSSL(8000, factory, myContextFactory)
reactor.run()

reactor.listenTCP(8000, ChatFactory())
reactor.run()
