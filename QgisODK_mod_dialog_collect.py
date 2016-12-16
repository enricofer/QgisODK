# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_collect.ui'
#
# Created: Thu Dec 15 11:36:41 2016
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

class Ui_dataCollectDialog(object):
    def setupUi(self, dataCollectDialog):
        dataCollectDialog.setObjectName(_fromUtf8("dataCollectDialog"))
        dataCollectDialog.resize(322, 551)
        self.verticalLayout = QtGui.QVBoxLayout(dataCollectDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.downloadCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.downloadCheckBox.setObjectName(_fromUtf8("downloadCheckBox"))
        self.verticalLayout.addWidget(self.downloadCheckBox)
        self.syncroCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.syncroCheckBox.setObjectName(_fromUtf8("syncroCheckBox"))
        self.verticalLayout.addWidget(self.syncroCheckBox)
        self.layerComboBox = QtGui.QComboBox(dataCollectDialog)
        self.layerComboBox.setEditable(False)
        self.layerComboBox.setObjectName(_fromUtf8("layerComboBox"))
        self.verticalLayout.addWidget(self.layerComboBox)
        self.fieldTable = QtGui.QTableWidget(dataCollectDialog)
        self.fieldTable.setColumnCount(3)
        self.fieldTable.setObjectName(_fromUtf8("fieldTable"))
        self.fieldTable.setRowCount(0)
        self.fieldTable.horizontalHeader().setVisible(True)
        self.fieldTable.horizontalHeader().setSortIndicatorShown(True)
        self.verticalLayout.addWidget(self.fieldTable)
        self.buttonBox = QtGui.QDialogButtonBox(dataCollectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dataCollectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dataCollectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dataCollectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dataCollectDialog)

    def retranslateUi(self, dataCollectDialog):
        dataCollectDialog.setWindowTitle(_translate("dataCollectDialog", "Import collected data", None))
        self.downloadCheckBox.setText(_translate("dataCollectDialog", "Download attachments", None))
        self.syncroCheckBox.setText(_translate("dataCollectDialog", "Syncronize with existing layer", None))

