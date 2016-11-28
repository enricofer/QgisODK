# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/enrico/Dropbox/dev/qgisODK/QgisODK_mod_dialog_base.ui'
#
# Created: Mon Nov 28 16:58:46 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from fields_tree import ODK_fields

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

class Ui_QgisODKDialogBase(object):
    def setupUi(self, QgisODKDialogBase):
        QgisODKDialogBase.setObjectName(_fromUtf8("QgisODKDialogBase"))
        QgisODKDialogBase.resize(754, 368)
        self.verticalLayout = QtGui.QVBoxLayout(QgisODKDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.layersComboBox = QtGui.QComboBox(QgisODKDialogBase)
        self.layersComboBox.setMinimumSize(QtCore.QSize(200, 0))
        self.layersComboBox.setObjectName(_fromUtf8("layersComboBox"))
        self.horizontalLayout_2.addWidget(self.layersComboBox)
        self.label = QtGui.QLabel(QgisODKDialogBase)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.settingsToolButton = QtGui.QToolButton(QgisODKDialogBase)
        self.settingsToolButton.setObjectName(_fromUtf8("settingsToolButton"))
        self.horizontalLayout_2.addWidget(self.settingsToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.treeView = ODK_fields(QgisODKDialogBase)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addGroupButton = QtGui.QPushButton(QgisODKDialogBase)
        self.addGroupButton.setObjectName(_fromUtf8("addGroupButton"))
        self.horizontalLayout.addWidget(self.addGroupButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.exportXlsFormButton = QtGui.QPushButton(QgisODKDialogBase)
        self.exportXlsFormButton.setObjectName(_fromUtf8("exportXlsFormButton"))
        self.horizontalLayout.addWidget(self.exportXlsFormButton)
        self.exportXFormButton = QtGui.QPushButton(QgisODKDialogBase)
        self.exportXFormButton.setObjectName(_fromUtf8("exportXFormButton"))
        self.horizontalLayout.addWidget(self.exportXFormButton)
        self.exportToWebServiceButton = QtGui.QPushButton(QgisODKDialogBase)
        self.exportToWebServiceButton.setObjectName(_fromUtf8("exportToWebServiceButton"))
        self.horizontalLayout.addWidget(self.exportToWebServiceButton)
        self.cancelButton = QtGui.QPushButton(QgisODKDialogBase)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(QgisODKDialogBase)
        QtCore.QMetaObject.connectSlotsByName(QgisODKDialogBase)

    def retranslateUi(self, QgisODKDialogBase):
        QgisODKDialogBase.setWindowTitle(_translate("QgisODKDialogBase", "QgisODK", None))
        self.label.setText(_translate("QgisODKDialogBase", "select Layer to Export to Open Data Kit format", None))
        self.settingsToolButton.setText(_translate("QgisODKDialogBase", "...", None))
        self.addGroupButton.setText(_translate("QgisODKDialogBase", "Add Group", None))
        self.exportXlsFormButton.setText(_translate("QgisODKDialogBase", "export to XlsForm", None))
        self.exportXFormButton.setText(_translate("QgisODKDialogBase", "export to XForm", None))
        self.exportToWebServiceButton.setText(_translate("QgisODKDialogBase", "export to Web Service", None))
        self.cancelButton.setText(_translate("QgisODKDialogBase", "Cancel", None))

