# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QgisODK_mod_dialog_collect.ui'
#
# Created: Tue Aug  1 14:50:26 2017
#      by: PyQt4 UI code generator 4.10.4
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
        self.syncroCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.syncroCheckBox.setObjectName(_fromUtf8("syncroCheckBox"))
        self.verticalLayout.addWidget(self.syncroCheckBox)
        self.layerComboBox = QtGui.QComboBox(dataCollectDialog)
        self.layerComboBox.setEditable(False)
        self.layerComboBox.setObjectName(_fromUtf8("layerComboBox"))
        self.verticalLayout.addWidget(self.layerComboBox)
        self.fieldTable = QtGui.QTableWidget(dataCollectDialog)
        self.fieldTable.setObjectName(_fromUtf8("fieldTable"))
        self.fieldTable.setColumnCount(3)
        self.fieldTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.fieldTable.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.fieldTable)
        self.downloadCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.downloadCheckBox.setObjectName(_fromUtf8("downloadCheckBox"))
        self.verticalLayout.addWidget(self.downloadCheckBox)
        self.progressBar = QtGui.QProgressBar(dataCollectDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.relativePathsCheckBox = QtGui.QCheckBox(dataCollectDialog)
        self.relativePathsCheckBox.setChecked(True)
        self.relativePathsCheckBox.setObjectName(_fromUtf8("relativePathsCheckBox"))
        self.verticalLayout.addWidget(self.relativePathsCheckBox)
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
        self.syncroCheckBox.setText(_translate("dataCollectDialog", "Syncronize with existing layer", None))
        item = self.fieldTable.horizontalHeaderItem(0)
        item.setText(_translate("dataCollectDialog", "uno", None))
        item = self.fieldTable.horizontalHeaderItem(1)
        item.setText(_translate("dataCollectDialog", "due", None))
        item = self.fieldTable.horizontalHeaderItem(2)
        item.setText(_translate("dataCollectDialog", "tre", None))
        self.downloadCheckBox.setText(_translate("dataCollectDialog", "Download attachments", None))
        self.relativePathsCheckBox.setText(_translate("dataCollectDialog", "Store project relative paths", None))

