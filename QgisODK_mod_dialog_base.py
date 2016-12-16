# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\qgisODK\QgisODK_mod_dialog_base.ui'
#
# Created: Wed Dec 07 14:33:14 2016
#      by: PyQt4 UI code generator 4.11.3
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
        QgisODKDialogBase.resize(881, 368)
        self.verticalLayout = QtGui.QVBoxLayout(QgisODKDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
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
        self.ODKsaveButton = QtGui.QToolButton(QgisODKDialogBase)
        self.ODKsaveButton.setMinimumSize(QtCore.QSize(24, 24))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKsaveButton.setIcon(icon)
        self.ODKsaveButton.setObjectName(_fromUtf8("ODKsaveButton"))
        self.horizontalLayout_2.addWidget(self.ODKsaveButton)
        self.ODKloadButton = QtGui.QToolButton(QgisODKDialogBase)
        self.ODKloadButton.setMinimumSize(QtCore.QSize(24, 24))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8("open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKloadButton.setIcon(icon1)
        self.ODKloadButton.setObjectName(_fromUtf8("ODKloadButton"))
        self.horizontalLayout_2.addWidget(self.ODKloadButton)
        self.settingsToolButton = QtGui.QToolButton(QgisODKDialogBase)
        self.settingsToolButton.setMinimumSize(QtCore.QSize(24, 24))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8("settings.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsToolButton.setIcon(icon2)
        self.settingsToolButton.setIconSize(QtCore.QSize(16, 16))
        self.settingsToolButton.setObjectName(_fromUtf8("settingsToolButton"))
        self.horizontalLayout_2.addWidget(self.settingsToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.treeView = ODK_fields(QgisODKDialogBase)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addGroupButton = QtGui.QPushButton(QgisODKDialogBase)
        self.addGroupButton.setObjectName(_fromUtf8("addGroupButton"))
        self.horizontalLayout.addWidget(self.addGroupButton)
        self.addFieldButton = QtGui.QPushButton(QgisODKDialogBase)
        self.addFieldButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.addFieldButton)
        self.removeFieldButton = QtGui.QPushButton(QgisODKDialogBase)
        self.removeFieldButton.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout.addWidget(self.removeFieldButton)
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
        self.importCollectedDataButton = QtGui.QPushButton(QgisODKDialogBase)
        self.importCollectedDataButton.setObjectName(_fromUtf8("importCollectedDataButton"))
        self.horizontalLayout.addWidget(self.importCollectedDataButton)
        self.cancelButton = QtGui.QPushButton(QgisODKDialogBase)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(QgisODKDialogBase)
        QtCore.QMetaObject.connectSlotsByName(QgisODKDialogBase)

    def retranslateUi(self, QgisODKDialogBase):
        QgisODKDialogBase.setWindowTitle(_translate("QgisODKDialogBase", "QgisODK", None))
        self.label.setText(_translate("QgisODKDialogBase", "select Layer to Export to Open Data Kit format", None))
        self.ODKsaveButton.setToolTip(_translate("QgisODKDialogBase", "save Open Data Kit project", None))
        self.ODKsaveButton.setText(_translate("QgisODKDialogBase", "S", None))
        self.ODKloadButton.setToolTip(_translate("QgisODKDialogBase", "load Open Data Kit Project", None))
        self.ODKloadButton.setText(_translate("QgisODKDialogBase", "L", None))
        self.settingsToolButton.setToolTip(_translate("QgisODKDialogBase", "Open Data Kit plugin general settings", None))
        self.settingsToolButton.setText(_translate("QgisODKDialogBase", "...", None))
        self.addGroupButton.setText(_translate("QgisODKDialogBase", "Add Group", None))
        self.addFieldButton.setText(_translate("QgisODKDialogBase", "Add Field", None))
        self.removeFieldButton.setText(_translate("QgisODKDialogBase", "Remove Field", None))
        self.exportXlsFormButton.setText(_translate("QgisODKDialogBase", "export to XlsForm", None))
        self.exportXFormButton.setText(_translate("QgisODKDialogBase", "export to XForm", None))
        self.exportToWebServiceButton.setText(_translate("QgisODKDialogBase", "export to Web Service", None))
        self.importCollectedDataButton.setText(_translate("QgisODKDialogBase", "import collected data", None))
        self.cancelButton.setText(_translate("QgisODKDialogBase", "Cancel", None))

