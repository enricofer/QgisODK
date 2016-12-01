# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_services.ui'
#
# Created: Wed Nov 30 13:01:27 2016
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

class Ui_ServicesDialog(object):
    def setupUi(self, ServicesDialog):
        ServicesDialog.setObjectName(_fromUtf8("ServicesDialog"))
        ServicesDialog.resize(328, 311)
        self.verticalLayout = QtGui.QVBoxLayout(ServicesDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabServices = QtGui.QTabWidget(ServicesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabServices.sizePolicy().hasHeightForWidth())
        self.tabServices.setSizePolicy(sizePolicy)
        self.tabServices.setMinimumSize(QtCore.QSize(310, 260))
        self.tabServices.setTabPosition(QtGui.QTabWidget.North)
        self.tabServices.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabServices.setDocumentMode(False)
        self.tabServices.setTabsClosable(False)
        self.tabServices.setMovable(False)
        self.tabServices.setObjectName(_fromUtf8("tabServices"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabServices.addTab(self.tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabServices)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.attachmentsCheckBox = QtGui.QCheckBox(ServicesDialog)
        self.attachmentsCheckBox.setObjectName(_fromUtf8("attachmentsCheckBox"))
        self.horizontalLayout.addWidget(self.attachmentsCheckBox)
        self.buttonBox = QtGui.QDialogButtonBox(ServicesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ServicesDialog)
        self.tabServices.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ServicesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ServicesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ServicesDialog)

    def retranslateUi(self, ServicesDialog):
        ServicesDialog.setWindowTitle(_translate("ServicesDialog", "ODK Services", None))
        self.tabServices.setTabText(self.tabServices.indexOf(self.tab), _translate("ServicesDialog", "Tab 1", None))
        self.attachmentsCheckBox.setText(_translate("ServicesDialog", "Download attachments", None))

