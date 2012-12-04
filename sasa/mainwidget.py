"""
Application's main widget
"""

from twisted.internet import reactor
from twisted.python import log

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from generated.ui_main import Ui_MainWidget
from generated import qrc_resource 
import main, settings


LOGIN = 0
MAIN = 1
        
class MainWidget(QWidget):
    
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        self.setupUi()
        self.connect_deferred = None
        
        ### Dialogs ###
        self.dlg_settings = settings.SettingsDialog(app)
        
    def setupUi(self):
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        
        self.ui.tb_settings.setIcon(QIcon(":/settings.png"))
        
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
        
        self.ui.btn_login_cancel.hide()
        
        self.connect(self.app, SIGNAL("SIG_CONNECTING"),
                     self.clientConnecting)
        self.connect(self.app, SIGNAL("SIG_CONNECTED"),
                     self.clientConnected)
        self.connect(self.app, SIGNAL("SIG_DISCONNECTING"),
                     self.clientDisconnecting)
        self.connect(self.app, SIGNAL("SIG_DISCONNECTED"),
                     self.clientDisconnected)
        
        self.connect(self.ui.tb_settings, SIGNAL("clicked()"),
                     self.onSettings)
        self.connect(self.ui.btn_login_connect, SIGNAL("clicked()"),
                     self.onConnect)
        self.connect(self.ui.btn_login_cancel, SIGNAL("clicked()"),
                     self.onCancelConnect)
        self.connect(self.ui.btn_login_register, SIGNAL("clicked()"),
                     self.onRegister)
        
        pos = self.app.settings.value("recent/pos").toPoint()
        size = self.app.settings.value("recent/size").toSize()
        self.move(pos)
        self.resize(size)
    
    ### UI handlers ###
    
    def onSettings(self):
        self.dlg_settings.show()
    
    def onConnect(self):
        username = str(self.ui.edit_login_userid.text())
        password = str(self.ui.edit_login_passwd.text())
        if self.ui.cb_login_type.isChecked():
            mode = "skey"
        else:
            mode = "sasl"
        self.connect_deferred = self.app.connect(username, password, mode)
        
    def onCancelConnect(self):
        if self.connect_deferred:
            self.connect_deferred.cancel()
            self.connect_deferred = None
        
    def onRegister(self):
        print 'onRegister'
    
    def onOffline(self):
        self.app.disconnect()
        
    ### Slots ###
    
    def clientConnecting(self):
        self.ui.lbl_error.clear()
        self.ui.pb_login.show()
        self.ui.btn_login_cancel.show()
        self.ui.btn_login_connect.hide()
        
    def clientConnected(self):
        self.ui.lbl_main_notification.setText("Available")
        self.ui.fr_settings.hide()
        self.ui.pb_login.hide()
        self.ui.btn_login_cancel.show()
        self.ui.btn_login_connect.show()
        self.ui.stacked_widget.setCurrentIndex(MAIN)
        self.connect_deferred = None
        
    def clientDisconnecting(self):
        pass
        
    def clientDisconnected(self, reason):
        log.msg(reason)
        if reason:
            self.ui.lbl_error.setText("<font color='red'>%s</font>" % reason)
        self.ui.fr_settings.show()
        self.ui.pb_login.reset()
        self.ui.pb_login.hide()
        self.ui.btn_login_cancel.hide()
        self.ui.btn_login_connect.show()
        self.ui.stacked_widget.setCurrentIndex(LOGIN)
        self.connect_deferred = None
    
    ### Events ###
    
    def showEvent(self, event):
        username = str(self.app.settings.value("recent/username").toString())
        if self.app.settings.value("recent/logintype", "sasl").toString() == "skey":
            self.ui.cb_login_type.setChecked(True)
        else:
            self.ui.cb_login_type.setChecked(False)
            
        if len(username) > 0:
            self.ui.edit_login_userid.setText(username)
            self.ui.edit_login_passwd.setFocus()
            
        if self.app.status == main.ST_OFFLINE:
            self.ui.stacked_widget.setCurrentIndex(LOGIN)
        
    def closeEvent(self, event):
        reactor.stop()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if self.ui.btn_login_connect.isEnabled():
                self.ui.btn_login_connect.animateClick()
                self.onConnect()
        else:
            QWidget.keyPressEvent(self, event)
        
    def moveEvent(self, event):
        self.app.settings.setValue("recent/pos", QWidget.pos(self))
        self.app.settings.setValue("recent/size", QWidget.size(self))
        
