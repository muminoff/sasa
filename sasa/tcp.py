from twisted.internet import reactor
from twisted.names.srvconnect import SRVConnector


class XMPPConnector(SRVConnector):
    
    def __init__(self, reactor, domain, factory, defaultPort):
        SRVConnector.__init__(self, reactor, 'xmpp-client', domain, factory, defaultPort)

    def pickServer(self):
        host, port = SRVConnector.pickServer(self)

        if not self.servers and not self.orderedServers:
            # no SRV record, fall back..
            port = 5222

        return host, port


class TCPConnector(object):
    
    def __init__(self, reactor, domain, factory):
        self.factory = factory
        self.domain = domain
        
    def connect(self):
        return reactor.connectTCP(self.domain, 5222, self.factory)
