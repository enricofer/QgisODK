# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_choices.ui'
#
# Created: Thu Dec 01 15:58:26 2016
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

class Ui_ChoicesDialog(object):
    def setupUi(self, ChoicesDialog):
        ChoicesDialog.setObjectName(_fromUtf8("ChoicesDialog"))
        ChoicesDialog.resize(296, 239)
        self.verticalLayout = QtGui.QVBoxLayout(ChoicesDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.choicesTable = QtGui.QTableWidget(ChoicesDialog)
        self.choicesTable.setObjectName(_fromUtf8("choicesTable"))
        self.choicesTable.setColumnCount(0)
        self.choicesTable.setRowCount(0)
        self.verticalLayout.addWidget(self.choicesTable)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.rowAddButton = QtGui.QToolButton(ChoicesDialog)
        self.rowAddButton.setMinimumSize(QtCore.QSize(25, 25))
        self.rowAddButton.setObjectName(_fromUtf8("rowAddButton"))
        self.horizontalLayout.addWidget(self.rowAddButton)
        self.rowRemoveButton = QtGui.QToolButton(ChoicesDialog)
        self.rowRemoveButton.setMinimumSize(QtCore.QSize(25, 25))
        self.rowRemoveButton.setObjectName(_fromUtf8("rowRemoveButton"))
        self.horizontalLayout.addWidget(self.rowRemoveButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ChoicesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ChoicesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ChoicesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ChoicesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ChoicesDialog)

    def retranslateUi(self, ChoicesDialog):
        ChoicesDialog.setWindowTitle(_translate("ChoicesDialog", "Value/label table", None))
        self.rowAddButton.setText(_translate("ChoicesDialog", "+", None))
        self.rowRemoveButton.setText(_translate("ChoicesDialog", "-", None))

