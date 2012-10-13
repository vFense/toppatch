#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import sys
import json
import jsonpickle

class EchoClient(LineReceiver):
    end="Bye-bye!"
    def connectionMade(self):
       r = jsonpickle.encode({"operation" : "send_csr", "csr" : "-----BEGIN CERTIFICATE REQUEST-----\nMIICmjCCAYICAQMwVTENMAsGA1UEAxMEdGVzdDEMMAoGA1UEChMDZm9vMQwwCgYD\nVQQLEwNmZWUxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJGTDEOMAwGA1UEBxMFRG9y\nYWwwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDqHsmhkydrTBq5EKyF\nqC4AGQKu9RBdiiT/t4aEUjj2D8/VDfmoyc3N0mtyhRwge25YFLIMVHhTY16GV8rl\nXyoAHc7/n5ZW34GyLKEXqAbPgufYAEvJQsg8DVud9AqAe2TA4JlTU14dfvzStH0U\nG8J7ayXfEYhce4Qw92Cywi8FoEwSzPd3lPKECk4RJBmMKUtL3MP2Omc4AU9NN01D\nK56cxyJ+Q9I60m8/IV1C8iL/bd96zf8DmvLuC7sH6XakveS/JFRLU0YufM6i0Xtd\nvgTSmvjrz5suHyKBv4RTPGvE6O3CYVzSjGd9oQQgFSshUWR4Yz+hNOGZThh5j0Dj\nrDkBAgMBAAGgADANBgkqhkiG9w0BAQ0FAAOCAQEAuJhT5VC4RLYgcIwtRjymUiHT\npmsFjUzWrVm4dmqrY2jQQ1yg1b7BiF8uMuwsCci0+0YYDMO9fxHYuKEFbMBSQmly\nLc77DmgmTfDjWInrQ4/1SuvSSS/DWo6lNDDEJTraJjQKIj1Xy9ZnDanjMctt5qnb\nXBKFxl2HBnfO0kyK1uuMB8DF9ZeCQ48ygr9c6ETHaLEIv8weNDh92+altbx3SGpw\ns5HDyRJxpePox/0LwZYe0oohKuUN8gW7wzywbQqIW/FWQhhE/fpw+8aMRVnIxFzV\nBrzBbEW79Lyhw+a9Yj/eNVvWxYPY3CqowBvKQT2ZoHJWBYphW+H2orciivg9bA==\n-----END CERTIFICATE REQUEST-----\n"})
       self.sendLine(r)
       self.transport.loseConnection()
        #self.sendLine("Hello, world!")
        #self.sendLine("What a fine day it is.")
        #self.sendLine(self.end)

    def lineReceived(self, line):
        print "receive:", line
        if line==self.end:
            self.transport.loseConnection()

class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    factory = EchoClientFactory()
    reactor.connectTCP('localhost', 8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
