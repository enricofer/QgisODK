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
import requests
import json
import time

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QTableWidget, QWidget, QTableWidgetItem, QSizePolicy
from PyQt4.QtCore import Qt, QSettings, QSize
from qgis.core import QgsProject, QgsMapLayerRegistry
from QgisODK_mod_dialog_base import Ui_QgisODKDialogBase
from QgisODK_mod_dialog_services import Ui_ServicesDialog
from QgisODK_mod_dialog_import import Ui_ImportDialog
from QgisODK_mod_dialog_choices import Ui_ChoicesDialog
from fields_tree import slugify
from dateutil.parser import parse

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'QgisODK_mod_dialog_base.ui'))


class QgisODKDialog(QtGui.QDialog, Ui_QgisODKDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(QgisODKDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        settingsIcon = QtGui.QIcon()
        settingsIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"settings.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsToolButton.setIcon(settingsIcon)
        saveIcon = QtGui.QIcon()
        saveIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKsaveButton.setIcon(saveIcon)
        loadIcon = QtGui.QIcon()
        loadIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"load.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKloadButton.setIcon(loadIcon)



class QgisODKChoices(QtGui.QDialog, Ui_ChoicesDialog):

    def __init__(self,choicesJson, parent = None):
        """Constructor."""
        super(QgisODKChoices, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.choicesDict = json.loads(choicesJson)
        self.choicesTable.setColumnCount(2)
        self.choicesTable.setRowCount(len(choicesDict))
        for i,choice in enumerate(choicesDict):
            print choice
            choiceValueWidget = QTableWidgetItem()
            choiceLabelWidget = QTableWidgetItem()
            choiceValueWidget.setData(Qt.EditRole,choice)
            choiceLabelWidget.setData(Qt.EditRole,choicesDict[choice])
            editorQWidget.setItem(i,0,choiceValueWidget)
            editorQWidget.setItem(i,1,choiceLabelWidget)
        self.choicesTable.setItem(i+1,0,QTableWidgetItem(""))
        self.choicesTable.setItem(i+1,1,QTableWidgetItem(""))
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.acceptedFlag = None
        
    def accept(self):
        choicesDict = {}
        for i in range(0,self.choicesTable.rowCount()):
            choicesDict[self.choicesTable.itemAt(i,0).data(Qt.EditRole)] = self.choicesTable.itemAt(i,1).data(Qt.EditRole)
        self.result = json.dumps(choicesDict)
        self.close()
        self.acceptedFlag = True
    
    def reject(self):
        self.close()
        self.acceptedFlag = None

    @staticmethod
    def getChoices(choicesJson,title=""):
        dialog = QgisODKChoices(choicesJson)
        dialog.setWindowTitle(title)
        result = dialog.exec_()
        dialog.show()
        if dialog.acceptedFlag:
            return (dialog.result)
        else:
            return (None)


class QgisODKImportCollectedData(QtGui.QDialog, Ui_ImportDialog):

    def __init__(self, module, parent = None):
        """Constructor."""
        self.iface = module.iface
        self.settingsDlg = module.settingsDlg
        print "PARENT:",self.iface,self.settingsDlg
        super(QgisODKImportCollectedData, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def show(self):
        availableData,response = self.settingsDlg.getAvailableDataCollections()
        print "availableData:",availableData
        if availableData:
            self.availableDataList.addItems(availableData)
        super(QgisODKImportCollectedData, self).show()
        self.raise_()
        
    def accept(self):
        geojsonDict,response = self.settingsDlg.getLayer(self.availableDataList.selectedItems()[0].text())
        if geojsonDict and response.status_code == requests.codes.ok:
            workDir = QgsProject.instance().readPath("./")
            geoJsonFileName = self.availableDataList.selectedItems()[0].text()+'_odk-'+time.strftime("%d-%m-%Y")+'.geojson'
            with open(os.path.join(workDir,geoJsonFileName), "w") as geojson_file:
                geojson_file.write(json.dumps(geojsonDict))
            layer = self.iface.addVectorLayer(os.path.join(workDir,geoJsonFileName), geoJsonFileName[:-8], "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            print 'CONTENT',response.status_code,response.reason,response.text
            
            '''
            currentLayerState = self.getDomDef(self.iface.legendInterface().currentLayer())
                
            currentFormConfig = currentLayer.editFormConfig() #recover
            fieldsModel = {}
            for i in range(0,len(currentLayer.pendingFields())):
                fieldsModel[currentLayer.pendingFields()[i].name()] = currentFormConfig.widgetType(i)
                
            layer.readLayerXML(currentLayerState)
            '''
        else:
            print response.text
            self.iface.messageBar().pushMessage("QgisODK plugin", "error loading csv table %s, %s." % (response.status_code,response.reason), level=QgsMessageBar.CRITICAL, duration=6)

        
    def reject(self):
        self.hide()

class QgisODKServices(QtGui.QDialog, Ui_ServicesDialog):

    services = [
        'ona', 'google'
    ]
    

    def __init__(self, parent = None):
        """Constructor."""
        super(QgisODKServices, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        for numServices in range (1,len(self.services)):
            container = QWidget()
            container.resize(QSize(310,260))
            self.tabServices.addTab(container,"")
        
        for tab,service in enumerate(self.services):
            container = self.tabServices.widget(tab)
            serviceClass = globals()[service]
            serviceClass(container)
            self.tabServices.setTabText(tab, service)
            
        S = QSettings()
        currentService = S.value("qgisodk/", defaultValue =  "0")
        self.tabServices.setCurrentIndex(int(currentService))
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getCurrentService(self):
        return self.tabServices.currentWidget().children()[0]

    def accept(self):
        self.getCurrentService().setup()
        self.hide()
    
    def getAvailableDataCollections(self):
        availableDataCollections,response = self.getCurrentService().getAvailableDataCollections()
        return availableDataCollections,response
    
    def reject(self):
        self.hide()
        
    def sendForm(self, xForm_id, xForm):
        response = self.getCurrentService().sendForm(xForm_id, xForm)
        return response
        
    def getLayer(self,layerName):
        geojsonDict,response = self.getCurrentService().getLayer(slugify(layerName))
        return  geojsonDict,response

class external_service(QTableWidget):
    
    def __init__(self, parent, parameters):
        super(external_service, self).__init__(parent)
        self.parent = parent
        self.resize(QSize(310,260))
        self.setColumnCount(2)
        self.setColumnWidth(0, 152)
        self.setColumnWidth(1, 152)
        self.setRowCount(len(parameters)-1)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        
        S = QSettings()
        for row,parameter in enumerate(parameters):
            if row == 0:
                self.service_id = parameter[1]
                continue
            row = row -1
            pKey = QTableWidgetItem (parameter[0])
            pKey.setFlags(pKey.flags() ^ Qt.ItemIsEditable)
            pValue = QTableWidgetItem (parameter[1])
            self.setItem(row,0,pKey)
            valueFromSettings = S.value("qgisodk/%s/%s/" % (self.service_id,self.item(row,0).text()), defaultValue =  "undef")
            if valueFromSettings == "undef":
                self.setItem(row,1,pValue)
                S.setValue("qgisodk/%s/%s/" % (self.service_id,self.item(row,0).text()),parameter[1])
            else:
                self.setItem(row,1,QTableWidgetItem (valueFromSettings))

    def setup(self):
        S = QSettings()
        print self.parent.parent().currentIndex()
        S.setValue("qgisodk/", self.parent.parent().currentIndex())
        for row in range (0,self.rowCount()):
            S.setValue("qgisodk/%s/%s/" % (self.service_id,self.item(row,0).text()),self.item(row,1).text())
        
    def getValue(self,key):
        if key == 'download_attachments':
            return self.parent.parent().parent().parent().attachmentsCheckBox.isChecked()
        for row in range (0,self.rowCount()):
            if self.item(row,0).text() == key:
                return self.item(row,1).text()
        raise AttributeError("key not found: " + key)
    
    def getAvailableDataCollections(self):
        url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        response = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.getValue("user"), self.getValue("password")), proxies = self.getProxiesConf())
        if response.status_code != requests.codes.ok:
            return None, response
        forms = response.json()
        availableDataCollections = []
        for form in forms:
            print "FORM:",form["id_string"]
            availableDataCollections.append(form["id_string"])
        print availableDataCollections
        return availableDataCollections,response
    
    def formIDToPk(self,xForm_id):
        #verify if form exists:
        url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        response = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.getValue("user"), self.getValue("password")), proxies = self.getProxiesConf())
        if response.status_code != requests.codes.ok:
            return None, response
        forms = response.json()
        form_key = None
        for form in forms:
            print form['sms_id_string']
            if form['sms_id_string'] == xForm_id:
                form_key = form['formid']
                break
        return form_key, response
    
    def getProxiesConf(self):
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

class ona(external_service):
    parameters = [
        ["id","ona.io"],
        ["name",""],
        ["project_id", ""],
        ["user", ""],
        ["password", ""],
    ]
    
    def __init__(self, parent):
        super(ona, self).__init__(parent,self.parameters)

    def sendForm(self, xForm_id, xForm):
        print "ID", xForm_id
        
        #step1 - verify if form exists:
        form_key, response = self.formIDToPk(xForm_id)
        print "RESPONSE:", response.status_code, "FORM_KEY:", form_key
        if response.status_code != requests.codes.ok:
            return response
        if form_key:
            method = 'PATCH'
            url = 'https://api.ona.io/api/v1/forms/%s' % form_key
        else:
            method = 'POST'
            url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        #step1 - upload form: POST if new PATCH if exixtent
        print url
        files = {'xls_file': (xForm, open(xForm, 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}
        response = requests.request(method, url, files=files, auth=requests.auth.HTTPBasicAuth(self.getValue("user"), self.getValue("password")), proxies = self.getProxiesConf())#, proxies = proxyDict,headers={'Content-Type': 'application/octet-stream'})
        return response

    def getJSON(self,xForm_id):
        #step1 - verify if form exists:
        form_key, response = self.formIDToPk(xForm_id)
        if response.status_code != requests.codes.ok:
            return response
        if form_key:
            url = 'https://api.ona.io/api/v1/data/%s' % form_key
            response = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.getValue("user"), self.getValue("password")))
            return response

    def guessGeomType(self,geom):
        coordinates = geom.split(';')
        firstCoordinate = coordinates[0].split(' ')
        coordinatesList = []
        for coordinate in coordinates:
            coordinatesList.append(coordinate.split(' '))
        if len(firstCoordinate) != 4:
            return "invalid", None
        if len(coordinates) == 1:
            return "Point", coordinatesList #geopoint
        if coordinates[-1] == '' and coordinatesList[0][0] == coordinatesList[-2][0] and coordinatesList[0][1] == coordinatesList[-2][1]:
            return "Polygon", coordinatesList #geoshape
        else:
            return "LineString", coordinatesList #geotrace

    def getLayer(self,xForm_id):
        remoteResponse = self.getJSON(xForm_id)
        print "GETLAYER1: ",remoteResponse.status_code, remoteResponse.reason
        if remoteResponse.status_code == requests.codes.ok:
            remoteData = remoteResponse.json()
            geojson = {
                "type": "FeatureCollection",
                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                "features": []
            }
            
            for record in remoteData:
                if 'GEOMETRY' in record:
                    geomType, geomCoordinates = self.guessGeomType(record['GEOMETRY'])
                    feature = {
                        "type": "Feature",
                         "properties": {},
                         "geometry": {
                            "type": geomType
                         }
                    }
                        
                    #build geojson geometry
                    jsonCoordinates = []
                    for geomCoordinate in geomCoordinates:
                        jsonCoordinates.append([float(geomCoordinate[1]),float(geomCoordinate[0])])
                    if geomType == 'Point':
                        feature["geometry"]["coordinates"] = [jsonCoordinates[0][0],jsonCoordinates[0][1]]
                    if geomType == 'LineString':
                        feature["geometry"]["coordinates"] = jsonCoordinates
                    if geomType == 'Polygon':
                        feature["geometry"]["coordinates"] = [jsonCoordinates]
                else:
                    feature = {
                        "type": "Feature",
                         "properties": {},
                         "geometry": None
                    }
                    
                #recode attachments:
                attachements = {}
                if '_attachments' in record:
                    for attachment in record['_attachments']:
                        fileKey = attachment["download_url"].split('/')[-1]
                        #todo local download attachment files if option is checked
                        attachements[fileKey] = 'https://api.ona.io' + attachment["download_url"]
                        if self.getValue("download_attachments") and QgsProject.instance().readPath("./") != "./":
                            downloadDir = os.path.join(QgsProject.instance().readPath("./"),'attachments_%s_%s' % (self.getValue("name"),self.getValue("project_id")))
                            if not os.path.exists(downloadDir):
                                os.makedirs(downloadDir)
                            response = requests.get(attachements[fileKey], stream=True)
                            localAttachmentPath = os.path.abspath(os.path.join(downloadDir,fileKey))
                            if response.status_code == 200:
                                print localAttachmentPath
                                with open(localAttachmentPath, 'wb') as f:
                                    for chunk in response:
                                        f.write(chunk)
                                    attachements[fileKey] = localAttachmentPath
                            else:
                                attachements[fileKey] = ''
                
                #build geojson properties
                for fieldKey, fieldValue in record.iteritems():
                    if not fieldKey in ('GEOMETRY','_attachments','_tags','_notes','_bamboo_dataset_id','_geolocation'): # field exclusion
                        if fieldValue in attachements.keys():
                            fieldValue = attachements[fieldValue]
                        feature["properties"][fieldKey] = fieldValue
                        
                geojson["features"].append(feature)
                
            print 
            return geojson, remoteResponse
        else:
            return None, remoteResponse

class google(external_service):
    parameters = [
        ["id","google drive"],
        ["sheet",""],
        ["drive key", ""],
        ["user", ""],
        ["password", ""],
    ]
    
    def __init__(self, parent):
        super(google, self).__init__(parent,self.parameters)