# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisODKDialog
                                 A QGIS plugin
 GeoODK integration for on-filed data collection
                             -------------------
        begin                : 2016-11-15
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Enrico Ferreguti
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import json

from PyQt4 import QtGui
from PyQt4.QtGui import QTableWidgetItem, QSizePolicy
from PyQt4.QtCore import Qt, QSize, QSettings, QTranslator, qVersion, QCoreApplication
from QgisODK_mod_dialog_choices import Ui_ChoicesDialog


class QgisODKChoices(QtGui.QDialog, Ui_ChoicesDialog):

    def __init__(self,choicesJson, valueType, parent = None):
        """Constructor."""
        super(QgisODKChoices, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.choicesJson = choicesJson
        choicesDict = json.loads(choicesJson)
        self.choicesTable.setColumnCount(2)
        self.choicesTable.setRowCount(len(choicesDict))
        self.choicesTable.verticalHeader().setVisible(False);
        self.choicesTable.setHorizontalHeaderItem(0, QTableWidgetItem("Values"))
        self.choicesTable.setHorizontalHeaderItem(1, QTableWidgetItem("Labels"))
        self.choicesTable.setColumnWidth(0, 127)
        self.choicesTable.setColumnWidth(1, 127)
        for i,choice in enumerate(choicesDict):
            print choice
            choiceValueWidget = QTableWidgetItem(valueType)
            choiceLabelWidget = QTableWidgetItem()
            choiceValueWidget.setData(Qt.EditRole,choice)
            choiceLabelWidget.setData(Qt.EditRole,choicesDict[choice])
            self.choicesTable.setItem(i,0,choiceValueWidget)
            self.choicesTable.setItem(i,1,choiceLabelWidget)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.rowAddButton.clicked.connect(self.rowAddAction)
        self.rowRemoveButton.clicked.connect(self.rowRemoveAction)
        
    def rowAddAction(self):
        if self.choicesTable.selectedItems():
            self.choicesTable.insertRow(self.choicesTable.selectedItems()[0].row())
        else:
            self.choicesTable.setRowCount(self.choicesTable.rowCount() + 1)
        
    def rowRemoveAction(self):
        if self.choicesTable.selectedItems():
            self.choicesTable.removeRow(self.choicesTable.selectedItems()[0].row())
    
    def getChoicesJson(self):
        choicesDict = {}
        for i in range(0,self.choicesTable.rowCount()):
            print self.choicesTable.item(i,0).data(Qt.EditRole)
            try:
                choicesDict[self.choicesTable.item(i,0).data(Qt.EditRole)] = self.choicesTable.item(i,1).data(Qt.EditRole)
            except:
                pass
        return json.dumps(choicesDict)
    
    def exreject(self):
        self.result = self.choicesJson
        self.close()
        self.acceptedFlag = None

    @staticmethod
    def getChoices(choicesJson, qType, title=""):
        dialog = QgisODKChoices(choicesJson, qType)
        dialog.setWindowTitle(title)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            return dialog.getChoicesJson()
        else:
            return choicesJson