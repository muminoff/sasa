"""
Application's main widget
"""

from twisted.internet import reactor

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from generated.ui_main import Ui_MainWidget


LOGIN = 0
MAIN = 1
        
class MainWidget(QWidget):
    
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        self.setupUi()
        
    def setupUi(self):
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        
        menu = QMenu(self.ui.tool_title)
        menu.addAction('Available')
        menu.addAction('Away')
        menu.addAction('Extended Away')
        
        action_offline = QAction('Offline', menu)
        menu.addAction(action_offline)
        self.connect(action_offline, SIGNAL("triggered()"),
                     self.onOffline)
        menu.addAction('Invisible')
        self.ui.tool_title.setMenu(menu)
        
        self.ui.pb_login.setMinimum(0)
        self.ui.pb_login.setMaximum(0)
        self.ui.pb_login.setVisible(False)
        
        self.connect(self.app, SIGNAL("SIG_CONNECTING"),
                     self.clientConnecting)
        self.connect(self.app, SIGNAL("SIG_CONNECTED"),
                     self.clientConnected)
        self.connect(self.app, SIGNAL("SIG_DISCONNECTING"),
                     self.clientDisconnecting)
        self.connect(self.app, SIGNAL("SIG_DISCONNECTED"),
                     self.clientDisconnected)
        
        self.connect(self.ui.btn_login_connect, SIGNAL("clicked()"),
                     self.onConnect)
        self.connect(self.ui.btn_login_register, SIGNAL("clicked()"),
                     self.onRegister)
    
    ### UI handlers
    
    def onConnect(self):
        self.ui.btn_login_connect.setDisabled(True)
        self.app.connect()
        
    def onRegister(self):
        print 'onRegister'
    
    def onOffline(self):
        self.app.disconnect()
        
    ### Slots ###
    
    def clientConnecting(self):
        self.ui.pb_login.setVisible(True)
        
    def clientConnected(self):
        self.ui.pb_login.setVisible(False)
        self.ui.btn_login_connect.setDisabled(False)
        self.ui.stacked_widget.setCurrentIndex(MAIN)
        
    def clientDisconnecting(self):
        print 'disconnecting'
        
    def clientDisconnected(self):
        self.ui.pb_login.reset()
        self.ui.pb_login.setVisible(False)
        self.ui.btn_login_connect.setDisabled(False)
        self.ui.stacked_widget.setCurrentIndex(LOGIN)
    
    ### Events ###
    
    def showEvent(self, event):
        username = str(self.app.settings.value("recent/username").toString())
        if len(username) > 0:
            self.ui.edit_login_userid.setText(username)
            self.ui.edit_login_passwd.setFocus()
        
    def closeEvent(self, event):
        reactor.stop()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if self.ui.btn_login_connect.isEnabled():
                self.ui.btn_login_connect.animateClick()
                self.onConnect()
        else:
            QWidget.keyPressEvent(self, event)
        