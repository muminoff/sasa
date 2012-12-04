"""
Application's settings dialog
"""

from twisted.internet import reactor
from twisted.python import log

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from generated.ui_settings import Ui_SettingsDialog

class SettingsDialog(QDialog):
    
    def __init__(self, app):
        QDialog.__init__(self)
        self.app = app
        self.setupUi()
        
    def setupUi(self):
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        
        self.connect(self.ui.bbox, SIGNAL("accepted()"), self.accept)
        self.connect(self.ui.bbox, SIGNAL("rejected()"), self.reject)
        
    def accept(self):
        self.app.settings.setValue("smartauth/apikey", self.ui.edit_api_key.text())
        self.app.settings.setValue("smartauth/domain", self.ui.edit_domain.text())
        QDialog.accept(self)
        
    def onReject(self):
        QDialog.reject(self)
    
    ### Events ###
    
    def showEvent(self, event):
        self.ui.edit_api_key.setText(self.app.settings.value("smartauth/apikey", "").toString())
        self.ui.edit_domain.setText(self.app.settings.value("smartauth/domain", "").toString())
        