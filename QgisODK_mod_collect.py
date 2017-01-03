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
import time
import requests

from PyQt4 import QtGui
from PyQt4.QtGui import QTableWidgetItem, QSizePolicy, QItemDelegate, QComboBox, QLineEdit, QFileDialog
from PyQt4.QtCore import Qt, QSize, QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo,QVariant
from QgisODK_mod_dialog_collect import Ui_dataCollectDialog

from qgis.core import QgsMapLayer, QgsMapLayerRegistry, QgsProject, QgsFeature, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPoint
from qgis.gui import QgsMessageBar

from fields_tree import slugify

class QgisODKimportDataFromService(QtGui.QDialog, Ui_dataCollectDialog):

    def __init__(self, module, parent = None):
        """Constructor."""
        self.iface = module.iface
        self.module = module
        super(QgisODKimportDataFromService, self).__init__(parent)
        self.setupUi(self)
        self.syncroCheckBox.stateChanged.connect(self.checkSyncroAction)
        self.downloadCheckBox.stateChanged.connect(self.checkDownloadAction)
        self.checkDownloadAction()
        self.fieldTable.setColumnCount(3)
        self.fieldTable.verticalHeader().setVisible(False)
        self.fieldTable.horizontalHeader().setVisible(True)
        self.fieldTable.setAlternatingRowColors(True)
        self.fieldTable.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("import")))
        self.fieldTable.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("ODK field")))
        self.fieldTable.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("map to Qgis field")))
        #self.fieldTable.setHorizontalHeaderLabels([self.tr("import"),self.tr("ODK field"),self.tr("map to Qgis field")])
        self.fieldTable.setColumnWidth(0,30)
        self.fieldTable.setColumnWidth(1,125)
        self.fieldTable.setColumnWidth(2,125)
        self.fieldTable.setItemDelegate(collectDelegate(self.fieldTable,self))
        self.collectedData = None
        self.fieldMapping = {}
        # initialize QTranslator
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QgisODK_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate('QgisODK', message)

    def checkDownloadAction(self):
        if self.downloadCheckBox.isChecked():
            self.relativePathsCheckBox.setEnabled(True)
        else:
            self.relativePathsCheckBox.setEnabled(False)

    def checkSyncroAction(self):
        if self.syncroCheckBox.isChecked():
            self.layerComboBox.setEnabled(True)
            try:
                self.layerComboBox.currentIndexChanged.disconnect(self.layerComboBoxChanged)
            except:
                pass
            self.layerComboBox.clear()
            for layer in self.iface.legendInterface().layers():
                if layer.type() == QgsMapLayer.VectorLayer:
                    self.layerComboBox.addItem(layer.name(),layer.id())
            if self.iface.legendInterface().currentLayer():
                current_idx = self.layerComboBox.findData(self.iface.legendInterface().currentLayer().id())
                if current_idx != -1:
                    self.layerComboBox.setCurrentIndex(current_idx)
            self.layerComboBox.currentIndexChanged.connect(self.layerComboBoxChanged)
            self.layerComboBoxChanged()
        else:
            self.layerComboBox.setEnabled(False)
            self.fieldMapping = {}
            for field in self.module.dlg.treeView.getFieldMappingDict().values():
                if field !='':
                    self.fieldMapping[slugify(field)] = field
            self.processingLayer = None
            self.populateFieldTable()

    def layerComboBoxChanged(self):
        '''
        if another layer is selected the currentlayerfields is updated 
        '''
        currentLayer = self.getCurrentLayer()
        currentLayerFields = {}
        for field in currentLayer.pendingFields():
            currentLayerFields[slugify(field.name())]=field.name() #dict with key slugified to simplify name match
        self.fieldMapping = currentLayerFields
        self.populateFieldTable()

    def getCurrentLayer(self):
        return QgsMapLayerRegistry.instance().mapLayer(self.layerComboBox.itemData(self.layerComboBox.currentIndex(),Qt.UserRole))

    def view(self, surveyName, collectedData):
        if collectedData:
            self.collectedDataDict = collectedData
            self.checkSyncroAction()
            self.show()
            self.raise_()
        else:
            self.collectedData = None

    def populateFieldTable(self):
        if self.collectedDataDict:
            importingFields = self.collectedDataDict[0].keys()
            self.fieldTable.clear()
            self.fieldTable.setRowCount(len(importingFields))
            predefinedFields = ['EOMETRY','ODKUUID']
            for row,field in enumerate(importingFields):
                enabledItem = QTableWidgetItem()
                enabledItem.setFlags(enabledItem.flags() | Qt.ItemIsUserCheckable)
                enabledItem.setText("")
                self.fieldTable.setItem(row,0,enabledItem)
                ODKfieldItem = QTableWidgetItem()
                ODKfieldItem.setText(field)
                self.fieldTable.setItem(row,1,ODKfieldItem)
                self.fieldTable.setRowHeight(row,30)
                QGISfieldItem = QTableWidgetItem()
                
                # try to guess field mapping
                QGISfieldItem.setText("")
                enabledItem.setCheckState(Qt.Unchecked)
                for fieldOrigin, FieldDest in self.fieldMapping.iteritems():
                    if fieldOrigin in slugify(field):
                        QGISfieldItem.setText(FieldDest)
                        enabledItem.setCheckState(Qt.Checked)
                        break

                '''
                if slugify(field) in self.fieldMapping:
                    QGISfieldItem.setText(self.fieldMapping[slugify(field)])
                    enabledItem.setCheckState(Qt.Checked)
                else:
                    QGISfieldItem.setText("")
                    enabledItem.setCheckState(Qt.Unchecked)
                '''

                self.fieldTable.setItem(row,2,QGISfieldItem)
                if field[-7:] in predefinedFields: #prevent predefined fields user editing
                    if field[-7:] == 'ODKUUID':
                        ODKfieldItem.setText('ODKUUID')
                        QGISfieldItem.setText('ODKUUID')
                    elif field[-7:] == 'EOMETRY':
                        ODKfieldItem.setText('GEOMETRY')
                        QGISfieldItem.setText('GEOMETRY')
                    enabledItem.setCheckState(Qt.Checked)
                    enabledItem.setFlags(enabledItem.flags() & Qt.ItemIsEditable)
                    ODKfieldItem.setFlags(ODKfieldItem.flags() & Qt.ItemIsEditable)
                    QGISfieldItem.setFlags(QGISfieldItem.flags() & Qt.ItemIsEditable)

    def getExportFieldMap(self):
        exportFieldMap = {}
        for row in range(0, self.fieldTable.rowCount()):
            if self.fieldTable.item(row,0).checkState() == Qt.Checked or self.fieldTable.item(row,1).text() == 'GEOMETRY':
                fieldSource = self.fieldTable.item(row,1).text()
                fieldTarget = self.fieldTable.item(row,2).text()
                exportFieldMap[fieldSource] = (fieldTarget or fieldSource)
        return exportFieldMap

    def accept(self):
        if self.collectedDataDict:
            exportMap = self.getExportFieldMap()
            cleanedDataDict = []
            for feature in self.collectedDataDict:
                cleanedFeat = {}
                for key,value in feature.iteritems():
                    if key == "GEOMETRY":
                        if "," in value: #geometry comes from google drive
                            value = value.replace(" ",";").replace(",", " ") # fixed comma/space/semicolon mismatch between odk aggregate and google drive
                        cleanedFeat["GEOMETRY"] = value
                    elif key[-7:] == "ODKUUID":
                        cleanedFeat["ODKUUID"] = value
                    elif key in exportMap:
                        cleanedFeat[exportMap[key]] = self.cleanURI(value) #Download and provide local URI if value is internet URI
                cleanedDataDict.append(cleanedFeat)
            if self.syncroCheckBox.isChecked():
                self.updateLayer(self.getCurrentLayer(),cleanedDataDict)
            else:
                geojsonDict = self.module.settingsDlg.getLayerFromTable(cleanedDataDict)
                if geojsonDict:
                    self.hide()
                    workDir = QgsProject.instance().readPath("./")
                    geoJsonFileName = QFileDialog().getSaveFileName(None, self.tr("Save as GeoJson"), workDir, "*.geojson")
                    if QFileInfo(geoJsonFileName).suffix() != "geojson":
                        geoJsonFileName += ".geojson"
                    with open(os.path.join(workDir,geoJsonFileName), "w") as geojson_file:
                        geojson_file.write(json.dumps(geojsonDict))
                    layer = self.iface.addVectorLayer(os.path.join(workDir,geoJsonFileName), QFileInfo(geoJsonFileName).baseName(), "ogr")
                    QgsMapLayerRegistry.instance().addMapLayer(layer)


    def cleanURI(self,URI):
        
        attachements = {}
        if isinstance(URI, basestring) and self.downloadCheckBox.isChecked() and (URI[0:7] == 'http://' or URI[0:8] == 'https://'):
            if self.processingLayer:
                layerName = self.processingLayer
            else:
                layerName = 'odk'
            fileName = URI.split('/')[-1]
            downloadDir = os.path.join(QgsProject.instance().readPath("./"),'attachments_%s' % layerName)
            if not os.path.exists(downloadDir):
                os.makedirs(downloadDir)
            response = requests.get(URI, stream=True)
            localAttachmentPath = os.path.abspath(os.path.join(downloadDir,fileName))
            if response.status_code == 200:
                print "downloading",localAttachmentPath, URI
                with open(localAttachmentPath, 'wb') as f:
                    for chunk in response:
                        f.write(chunk)
                    localURI = localAttachmentPath
                if self.relativePathsCheckBox.isChecked():
                    return os.path.relpath(localURI,QgsProject.instance().readPath("./"))
                else:
                    return localURI
            else:
                print 'error downloading remote file: ',response.reason
                return 'error downloading remote file: ',response.reason
        else:
            return URI


    def updateLayer(self,layer,dataDict):
        self.processingLayer = layer

        uuid_found = None
        for field in layer.pendingFields():
            if field.name() == 'ODKUUID':
                uuid_found = True

        if not uuid_found:
            uuidField = QgsField("ODKUUID", QVariant.String)
            uuidField.setLength(50)
            layer.dataProvider().addAttributes([uuidField])
            layer.updateFields()

        QgisFieldsList = [field.name() for field in layer.pendingFields()]
        #layer.beginEditCommand("ODK syncronize")
        layer.startEditing()
        
        uuidList = []
        for qgisFeature in layer.getFeatures():
            if qgisFeature['ODKUUID']:
                uuidList.append(qgisFeature['ODKUUID'])

        newQgisFeatures = []
        fieldError = None
        for odkFeature in dataDict:
            if not odkFeature['ODKUUID'] in uuidList:
                qgisFeature = QgsFeature()
                wktGeom = self.guessWKTGeomType(odkFeature['GEOMETRY'])
                qgisGeom = QgsGeometry.fromWkt(wktGeom)
                qgisFeature.setGeometry(qgisGeom)
                qgisFeature.initAttributes(len(QgisFieldsList))
                for fieldName, fieldValue in odkFeature.iteritems():
                    if fieldName != 'GEOMETRY':
                        try:
                            qgisFeature.setAttribute(QgisFieldsList.index(fieldName),fieldValue)
                        except:
                            fieldError = fieldName
                        
                newQgisFeatures.append(qgisFeature)
                
        if fieldError:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("Can't find '%s' field") % fieldError, level=QgsMessageBar.WARNING, duration=6)
        
        layer.addFeatures(newQgisFeatures)
        self.processingLayer = None


    def guessWKTGeomType(self,geom):
        coordinates = geom.split(';')
        firstCoordinate = coordinates[0].strip().split(" ")
        if len(firstCoordinate) < 2:
            return "invalid", None
        coordinatesList = []
        for coordinate in coordinates:
            decodeCoord = coordinate.strip().split(" ")
            coordinatesList.append([decodeCoord[0],decodeCoord[1]])
        if len(coordinates) == 1:
            
            reprojectedPoint = self.transformToLayerSRS(QgsPoint(float(coordinatesList[0][1]),float(coordinatesList[0][0])))
            return "POINT(%s %s)" % (reprojectedPoint.x(), reprojectedPoint.y()) #geopoint
        else:
            coordinateString = ""
            for coordinate in coordinatesList:
                reprojectedPoint = self.transformToLayerSRS(QgsPoint(float(coordinate[1]), float(coordinate[0])))
                coordinateString += "%s %s," % (reprojectedPoint.x(), reprojectedPoint.y())
            coordinateString = coordinateString[:-1]
        if coordinates[-1] == '' and coordinatesList[0][0] == coordinatesList[-2][0] and coordinatesList[0][1] == coordinatesList[-2][1]:
            return "POLYGON(%s)" % coordinateString #geoshape #geotrace
        else:
            return "LINESTRING(%s)" % coordinateString

    def reject(self):
        self.hide()

    def transformToLayerSRS(self, pPoint):
        # transformation from the current SRS to WGS84
        crsDest = self.processingLayer.crs () # get layer crs
        crsSrc = QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = QgsCoordinateTransform(crsSrc, crsDest)
        return xform.transform(pPoint) # forward transformation: src -> dest


class collectDelegate(QItemDelegate):

    def __init__(self, parent, module):
        self.module = module
        QItemDelegate.__init__(self, parent)

    def createEditor (self, parent, option, index):
        column = index.column()
        self.index = index
        content = index.model().data(index, Qt.EditRole)
        if column == 2:
            self.content = index.model().data(index, Qt.EditRole)
            self.editorQWidget = QComboBox(parent)
            self.editorQWidget.setEditable(True)
            self.editorQWidget.addItems(self.module.fieldMapping.values())
            if self.content in self.module.fieldMapping.values():
                self.editorQWidget.setCurrentIndex(self.editorQWidget.findData(self.content))
            else:
                self.editorQWidget.insertItem(0,'')
                self.editorQWidget.setCurrentIndex(0)
            return self.editorQWidget
        else:
            return None
            return QItemDelegate.createEditor(self, parent, option, index)