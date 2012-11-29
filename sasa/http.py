"""
HTTP utilities
"""
from zope.interface import implements

from twisted.internet import protocol, defer
from twisted.web.iweb import IBodyProducer



class HTTPResponseHandler(protocol.Protocol):
    
    def __init__(self, finished):
        self.finished = finished
        self.data = []
        
    def dataReceived(self, data):
        self.data.append(data)
        
    def connectionLost(self, reason):
        self.finished.callback(''.join(self.data))
        

class HTTPBodyProducer(object):
    implements(IBodyProducer)
    
    def __init__(self, data):
        self.data = data
        self.length = len(data)
        
    def startProducing(self, consumer):
        consumer.write(self.data)
        return defer.succeed(None)
    
    def pauseProducting(self):
        pass
    
    def stopProducing(self):
        pass
        