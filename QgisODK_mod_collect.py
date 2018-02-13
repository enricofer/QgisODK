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
    
def getProxiesConf():
    s = QSettings() #getting proxy from qgis options settings
    proxyEnabled = s.value("proxy/proxyEnabled", "")
    proxyType = s.value("proxy/proxyType", "" )
    proxyHost = s.value("proxy/proxyHost", "" )
    proxyPort = s.value("proxy/proxyPort", "" )
    proxyUser = s.value("proxy/proxyUser", "" )
    proxyPassword = s.value("proxy/proxyPassword", "" )
    if proxyEnabled == "true" and proxyType == 'HttpProxy': # test if there are proxy settings
        proxyDict = {
            "http"  : "http://%s:%s@%s:%s" % (proxyUser,proxyPassword,proxyHost,proxyPort),
            "https" : "http://%s:%s@%s:%s" % (proxyUser,proxyPassword,proxyHost,proxyPort) 
        }
        return proxyDict
    else:
        return None

class QgisODKimportDataFromService(QtGui.QDialog, Ui_dataCollectDialog):

    def __init__(self, service, parent = None):
        """Constructor."""
        self.service = service
        self.module = service.module
        self.iface = self.module.iface
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
        self.progressBar.setAlignment(Qt.AlignCenter)
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
            if self.module.dlg.treeView.getFieldMappingDict():
                target_fields = self.module.dlg.treeView.getFieldMappingDict().values()
            else:
                target_fields = self.collectedDataDict[0].keys()
            for field in target_fields:
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
        if currentLayer:
            for field in currentLayer.pendingFields():
                currentLayerFields[slugify(field.name())]=field.name() #dict with key slugified to simplify name match
            self.fieldMapping = currentLayerFields
        self.populateFieldTable()

    def getCurrentLayer(self):
        return QgsMapLayerRegistry.instance().mapLayer(self.layerComboBox.itemData(self.layerComboBox.currentIndex(),Qt.UserRole))

    def view(self, surveyName, collectedData):
        self.progressBar.hide()
        self.buttonBox.setEnabled(True)
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
            predefinedFields = ['EOMETRY','UUID']
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
                for predef in predefinedFields:
                    if predef in field.upper(): #prevent predefined fields user editing
                        if predef == 'UUID':
                            ODKfieldItem.setText(field)
                            QGISfieldItem.setText('ODKUUID')
                        elif predef == 'EOMETRY':
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
        print exportFieldMap
        if 'GEOMETRY' in exportFieldMap.values():
            return exportFieldMap
        else:
            return None

    def accept(self):
        if self.collectedDataDict:
            exportMap = self.getExportFieldMap()
            if not exportMap:
                self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("No 'GEOMETRY' field in field mapping, can't import ODK layer") , level=QgsMessageBar.WARNING, duration=6)
                return
            cleanedDataDict = []
            if self.syncroCheckBox.isChecked():
                self.processingLayer = self.getCurrentLayer()
                processingLayer_uuid_list = self.getUUIDList(self.processingLayer)
                baseDir = os.path.abspath(QgsProject.instance().readPath("./"))
            else:
                workDir = QgsProject.instance().readPath("./")
                geoJsonFileName = QFileDialog().getSaveFileName(None, self.tr("Save as GeoJson"), workDir, "*.geojson")
                if not geoJsonFileName:
                    return
                baseDir = os.path.dirname(geoJsonFileName)

            self.progressBar.setRange(0,len(self.collectedDataDict))
            self.progressBar.show()
            self.buttonBox.setEnabled(False)
            count = 1
            for feature in self.collectedDataDict:
                cleanedFeat = {}
                self.progressBar.setValue(count)

                if self.syncroCheckBox.isChecked():
                    feature_uuid = None
                    for key,value in feature.iteritems():
                        if "UUID" in key.upper():
                            #print "OK"
                            feature_uuid = value
                    if feature_uuid in processingLayer_uuid_list: #excluding already synced features 
                        #print "exclude feature ", feature_uuid
                        continue
                 
                for key,value in feature.iteritems():
                    if key == "GEOMETRY":
                        if "," in value: #geometry comes from google drive
                            value = value.replace(" ",";").replace(",", " ") # fixed comma/space/semicolon mismatch between odk aggregate and google drive
                        cleanedFeat["GEOMETRY"] = value
                    elif "UUID" in key.upper(): #key[-7:] == "ODKUUID"
                        cleanedFeat["ODKUUID"] = value
                    elif key in exportMap:
                        cleanedFeat[exportMap[key]] = self.cleanURI(value,baseDir,self.progressBar) #Download and provide local URI if value is internet URI
                
                count += 1
                cleanedDataDict.append(cleanedFeat)
                
            if self.syncroCheckBox.isChecked():
                self.updateLayer(self.getCurrentLayer(),cleanedDataDict)
            else:
                geojsonDict = self.module.settingsDlg.getLayerFromTable(cleanedDataDict)
                if geojsonDict:
                    self.hide()
                    if QFileInfo(geoJsonFileName).suffix() != "geojson":
                        geoJsonFileName += ".geojson"
                    with open(os.path.join(workDir,geoJsonFileName), "w") as geojson_file:
                        geojson_file.write(json.dumps(geojsonDict))
                    layer = self.iface.addVectorLayer(os.path.join(workDir,geoJsonFileName), QFileInfo(geoJsonFileName).baseName(), "ogr")
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    
            self.progressBar.setValue(count)
            self.buttonBox.setEnabled(True)
                    


    def cleanURI(self,URI,download_base_dir,widget = None):
        attachements = {}
        #print URI,download_base_dir,widget
        if isinstance(URI, basestring) and self.downloadCheckBox.isChecked() and (URI[0:7] == 'http://' or URI[0:8] == 'https://'):
            if self.processingLayer:
                layerName = self.processingLayer.name()
            else:
                layerName = 'odk'
            fileName = URI.split('/')[-1]
            if widget:
                progress = int(((widget.value()-widget.minimum())*100)/((widget.maximum()-widget.minimum())))
                widget.setFormat("%s %d%%" % (fileName,progress));
            downloadDir = os.path.join(download_base_dir,'attachments_%s' % layerName)
            if not os.path.exists(downloadDir):
                os.makedirs(downloadDir)
            return self.service.downloadMedia(URI,downloadDir)
        elif URI == 'n/a':
            return None
        else:
            return URI

    def getUUIDList(self,lyr):
        uuidList = []
        if lyr:
            uuidFieldName = None
            for field in lyr.pendingFields():
                if 'UUID' in field.name().upper():
                    uuidFieldName = field.name()
            if uuidFieldName:
                for qgisFeature in lyr.getFeatures():
                    uuidList.append(qgisFeature[uuidFieldName])
        return uuidList

    def updateLayer(self,layer,dataDict):
        #print "UPDATING N.",len(dataDict),'FEATURES'
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
        
        uuidList = self.getUUIDList(self.processingLayer)

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
        row = index.row()
        self.index = index
        content = index.model().data(index, Qt.EditRole)
        if column == 2:
            content = index.model().data(index, Qt.EditRole)
            label = index.model().data(index.model().index(row,1), Qt.EditRole)
            checkrowIndex = index.model().index(row,0)
            checkrowIndex = index.model().data(index.model().index(row,0), Qt.CheckStateRole)
            self.editorQWidget = QComboBox(parent)
            self.editorQWidget.setEditable(True)
            self.editorQWidget.addItems(self.module.fieldMapping.values())
            self.editorQWidget.addItems(['GEOMETRY','ODKUUID'])
            if content in self.module.fieldMapping.values():
                self.editorQWidget.setCurrentIndex(self.editorQWidget.findData(content))
                #self.module.fieldTable.item(row,0).setCheckState(Qt.Checked)
            else:
                #self.editorQWidget.insertItem(0,label)
                self.editorQWidget.insertItem(0,'')
                #self.module.fieldTable.item(row,0).setCheckState(Qt.Unchecked)
                self.editorQWidget.setCurrentIndex(0)
            return self.editorQWidget
        else:
            return None
        return QItemDelegate.createEditor(self, parent, option, index)