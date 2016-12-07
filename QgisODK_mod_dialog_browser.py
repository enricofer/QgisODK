# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_browser.ui'
#
# Created: Mon Dec 05 14:11:33 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AuthBrowser(object):
    def setupUi(self, AuthBrowser):
        AuthBrowser.setObjectName(_fromUtf8("AuthBrowser"))
        AuthBrowser.resize(831, 500)
        self.verticalLayout = QtGui.QVBoxLayout(AuthBrowser)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.webView = QtWebKit.QWebView(AuthBrowser)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)
        self.buttonBox = QtGui.QDialogButtonBox(AuthBrowser)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AuthBrowser)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AuthBrowser.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AuthBrowser.reject)
        QtCore.QMetaObject.connectSlotsByName(AuthBrowser)

    def retranslateUi(self, AuthBrowser):
        AuthBrowser.setWindowTitle(_translate("AuthBrowser", "Authentication", None))

from PyQt4 import QtWebKit
