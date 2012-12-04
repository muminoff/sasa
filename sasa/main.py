"""
Application controller.
"""

from PyQt4.QtCore import QObject, QSettings, SIGNAL

import mainwidget
import xmpp
import http

import json
from twisted.python import log
from twisted.words.protocols.jabber import jid
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet import reactor, defer
from twisted.internet.error import ConnectionRefusedError

ST_OFFLINE = 0
ST_CONNECTING = 1
ST_ONLINE = 2
ST_IDLE = 3
ST_DISCONNECTING = 4


class Application(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        self.status = ST_OFFLINE
        self.connector = None
        self.main_widget = mainwidget.MainWidget(self)
        self.initSettings()
        self.client = None
        
    def initSettings(self):
        self.settings = QSettings(QSettings.IniFormat,
                                  QSettings.UserScope,
                                  "SmartNet",
                                  "Sasa");
                                  
    ### API ###
    
    def showWindow(self):
        if self.status == ST_OFFLINE:
            self.main_widget.ui.stacked_widget.setCurrentIndex(mainwidget.LOGIN)
        self.main_widget.show()
    
    def startedConnecting(self, connector):
        self.emit(SIGNAL("SIG_CONNECTING"))

    def connect(self):
        if self.status == ST_OFFLINE:
            self.status = ST_CONNECTING
            if self.client:
                self.client.disconnect()
                    
            username = str(self.main_widget.ui.edit_login_userid.text())
            password = str(self.main_widget.ui.edit_login_passwd.text())
            if self.main_widget.ui.cb_login_type.isChecked():
                mode = "skey"
            else:
                mode = "sasl"
            self.settings.setValue("recent/username", username)
            self.settings.setValue("recent/logintype", mode)
            self.emit(SIGNAL("SIG_CONNECTING"))

            if mode == "skey":
                            
                ## get skey from profile
                
                def onBody(body):
                    if body:
                        data = json.loads(body)
                        log.msg('password', data['skey'])
                        self.client = xmpp.Client(self, jid.JID(username), data['skey'])
                        self.client.connect()
                
                def cb(response):
                    finished = defer.Deferred()
                    response.deliverBody(http.HTTPResponseHandler(finished))
                    return finished
                    
                def err(f):
                    r = f.trap(ConnectionRefusedError)
                    if r == ConnectionRefusedError:
                        self.main_widget.ui.lbl_error.setText("Can't connect to AS server")
                    else:
                        self.main_widget.ui.lbl_error.setText("Unknown error")
                    self.status = ST_OFFLINE
                    self.emit(SIGNAL("SIG_DISCONNECTED"))
                    
                agent = Agent(reactor)
                body = json.dumps({'api_key': 'qwerty123456',
                    'username': username,
                    'password': password})
                bodyProducer = http.HTTPBodyProducer(body)
                d = agent.request("POST",
                        "http://localhost:8000/api/skey",
                        headers=Headers({
                            'Accept': ['application/json'],
                            'Content-Type': ['application/json']
                             }),
                        bodyProducer=bodyProducer)
                
                d.addCallbacks(cb, err)
                d.addCallbacks(onBody, log.err)
                return d
     
            else:
                self.client = xmpp.Client(self, jid.JID(username), password)
                self.client.connect()
        
    def disconnect(self):
        if self.status not in (ST_OFFLINE, ST_DISCONNECTING):
            self.status = ST_DISCONNECTING
            self.client.disconnect()
            self.emit(SIGNAL("SIG_DISCONNECTING"))

    def clientConnected(self):
        self.status = ST_ONLINE
        self.main_widget.ui.lbl_main_notification.setText("Available")
        self.emit(SIGNAL("SIG_CONNECTED"))
        
    def clientDisconnected(self):
        self.status = ST_OFFLINE
        self.emit(SIGNAL("SIG_DISCONNECTED"))
    