"""
XMPP-specific
"""

from twisted.internet import reactor
from twisted.python import log
from twisted.words.protocols.jabber import xmlstream, client
from twisted.words.xish import domish
import tcp


class Client(object):
    def __init__(self, app, client_jid, secret):
        self.app = app
        self.factory = client.XMPPClientFactory(client_jid, secret)
        self.factory.addBootstrap(xmlstream.STREAM_CONNECTED_EVENT, self.connected)
        self.factory.addBootstrap(xmlstream.STREAM_END_EVENT, self.disconnected)
        self.factory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authenticated)
        self.factory.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.initFailed)
        self.connector = tcp.XMPPConnector(reactor, client_jid.host, self.factory,
                                           defaultPort=5222)
        
        self.iq_ctr = 0
        
    def connect(self):
        self.connector.connect()
        
    def disconnect(self):
        self.factory.stopTrying()
        self.connector.disconnect()

    def rawDataIn(self, buf):
        log.msg("RECV: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace'))

    def rawDataOut(self, buf):
        log.msg("SEND: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace'))

    def connected(self, xs):
        log.msg('Connected.')

        self.xmlstream = xs

        # Log all traffic
        xs.rawDataInFn = self.rawDataIn
        xs.rawDataOutFn = self.rawDataOut

    def disconnected(self, xs):
        log.msg('Disconnected.')
        self.app.clientDisconnected()

    def authenticated(self, xs):
        log.msg("Authenticated.")

        xs.setDispatchFn(self.onElement)
        self.app.clientConnected()
        
        roster = domish.Element((None, 'iq'))
        roster['id'] = 'iq_%d' % self.getNextIqCounter()
        roster['type'] = 'get'
        roster.addElement('query', 'jabber:iq:roster')
        xs.send(roster)
        
        presence = domish.Element((None, 'presence'))
        xs.send(presence)

    def initFailed(self, failure):
        log.msg("Initialization failed.")
        log.err(failure)

        self.xmlstream.sendFooter()
        self.disconnect()
            
    def onElement(self, el):
        print "onElement"
        
    ### Utils ###
    
    def getNextIqCounter(self):
        self.iq_ctr = self.iq_ctr + 1
        return self.iq_ctr
    
