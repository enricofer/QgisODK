# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_collect.ui'
#
# Created: Mon Dec 19 11:05:12 2016
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
        self.buttonBox = QtGui.QDialogButtonBox(dataCollectDialog)
        self.buttonBox.setGeometry(QtCore.QRect(9, 517, 160, 25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.syncroCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.syncroCheckBox.setGeometry(QtCore.QRect(9, 9, 166, 18))
        self.syncroCheckBox.setObjectName(_fromUtf8("syncroCheckBox"))
        self.layerComboBox = QtGui.QComboBox(dataCollectDialog)
        self.layerComboBox.setGeometry(QtCore.QRect(9, 33, 301, 20))
        self.layerComboBox.setEditable(False)
        self.layerComboBox.setObjectName(_fromUtf8("layerComboBox"))
        self.downloadCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.downloadCheckBox.setGeometry(QtCore.QRect(9, 469, 134, 18))
        self.downloadCheckBox.setObjectName(_fromUtf8("downloadCheckBox"))
        self.relativePathsCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.relativePathsCheckBox.setGeometry(QtCore.QRect(9, 493, 156, 18))
        self.relativePathsCheckBox.setChecked(True)
        self.relativePathsCheckBox.setObjectName(_fromUtf8("relativePathsCheckBox"))
        self.fieldTable = QtGui.QTableWidget(dataCollectDialog)
        self.fieldTable.setGeometry(QtCore.QRect(9, 59, 301, 401))
        self.fieldTable.setObjectName(_fromUtf8("fieldTable"))
        self.fieldTable.setColumnCount(3)
        self.fieldTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(2, item)

        self.retranslateUi(dataCollectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dataCollectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dataCollectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dataCollectDialog)

    def retranslateUi(self, dataCollectDialog):
        dataCollectDialog.setWindowTitle(_translate("dataCollectDialog", "Import collected data", None))
        self.syncroCheckBox.setText(_translate("dataCollectDialog", "Syncronize with existing layer", None))
        self.downloadCheckBox.setText(_translate("dataCollectDialog", "Download attachments", None))
        self.relativePathsCheckBox.setText(_translate("dataCollectDialog", "Store project relative paths", None))
        item = self.fieldTable.horizontalHeaderItem(0)
        item.setText(_translate("dataCollectDialog", "uno", None))
        item = self.fieldTable.horizontalHeaderItem(1)
        item.setText(_translate("dataCollectDialog", "due", None))
        item = self.fieldTable.horizontalHeaderItem(2)
        item.setText(_translate("dataCollectDialog", "tre", None))

