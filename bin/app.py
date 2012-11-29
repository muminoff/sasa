#!/usr/bin/env python

import os
import sys

def main():
    ## Import PyQt stuff
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QApplication

    ## init Qt app
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontShowIconsInMenus, False)
    app.setQuitOnLastWindowClosed(True)

    # init Twisted reactor
    from qt4reactor import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    # start logging
    from twisted.python import log
    log.startLogging(sys.stdout)

    # init our app
    from sasa import main

    main = main.Application()
    main.showWindow()

    # run reactor
    reactor.run()
    print "Bye"

if __name__ == "__main__":
    import app
    sys.path.append(os.path.dirname(app.__file__) + "/../")
    app.main()
    
