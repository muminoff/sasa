"""
Application controller.
"""

from PyQt4.QtCore import QObject, QSettings, SIGNAL

import mainwidget
import xmpp

from twisted.python import log
from twisted.words.protocols.jabber import jid

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
        
    def connect(self):
        if self.status == ST_OFFLINE:
            self.status = ST_CONNECTING
            if self.client:
                self.client.disconnect()
            username = str(self.main_widget.ui.edit_login_userid.text())
            password = str(self.main_widget.ui.edit_login_passwd.text())
            self.settings.setValue("recent/username", username)
            self.client = xmpp.Client(self, jid.JID(username), password)
            self.client.connect()
            self.emit(SIGNAL("SIG_CONNECTING"))
        
    def disconnect(self):
        if self.status not in (ST_OFFLINE, ST_DISCONNECTING):
            self.status = ST_DISCONNECTING
            self.client.disconnect()
            self.emit(SIGNAL("SIG_DISCONNECTING"))

    def clientConnected(self):
        self.status = ST_ONLINE
        self.main_widget.ui.edit_login_passwd.clear()
        self.main_widget.ui.lbl_main_notification.setText("Available")
        self.emit(SIGNAL("SIG_CONNECTED"))
        
    def clientDisconnected(self):
        self.status = ST_OFFLINE
        self.emit(SIGNAL("SIG_DISCONNECTED"))
        