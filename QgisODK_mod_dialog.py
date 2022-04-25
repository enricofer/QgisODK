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

 portions of odk_aggregate class is
        copyright            : (C) 2017 by IIRS - https://github.com/shivareddyiirs
        email                : kotishiva@gmail.com
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
import re
import base64
import csv
from io import StringIO

import xml.etree.ElementTree as ET

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QTableWidget, QWidget, QTableWidgetItem, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QSettings, QSize, QSettings, QTranslator, qVersion, QCoreApplication, QTimer, QUrl
from qgis.core import QgsProject, QgsNetworkAccessManager, Qgis
from qgis.gui import QgsMessageBar
from email.mime.text import MIMEText


from .QgisODK_mod_collect import QgisODKimportDataFromService, getProxiesConf

from .fields_tree import slugify, ODK_fields
from dateutil.parser import parse

Ui_QgisODKDialogBase, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'QgisODK_mod_dialog_base.ui'))
Ui_InternalBrowser, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'QgisODK_mod_dialog_browser.ui'))
Ui_ImportDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'QgisODK_mod_dialog_import.ui'))
Ui_ServicesDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'QgisODK_mod_dialog_services.ui'))

class QgisODKDialog(QtWidgets.QDialog, Ui_QgisODKDialogBase):
    def __init__(self, parentClass, parent=None):
        """Constructor."""
        super(QgisODKDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        #self.treeView = ODK_fields(self)
        #treeViewLayout = self.findChild(QtWidgets.QVBoxLayout, 'treeViewLayout')
        #treeViewLayout.addChildWidget(self.treeView)
        self.treeView.setObjectName("treeView")
        self.treeView.setIface(parentClass.iface)
        settingsIcon = QtGui.QIcon()
        settingsIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"settings.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsToolButton.setIcon(settingsIcon)
        saveIcon = QtGui.QIcon()
        saveIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKsaveButton.setIcon(saveIcon)
        loadIcon = QtGui.QIcon()
        loadIcon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__),"load.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ODKloadButton.setIcon(loadIcon)


class internalBrowser(QtWidgets.QDialog, Ui_InternalBrowser):

    def __init__(self, target, parent = None):
        super(internalBrowser, self).__init__(parent)
        self.setupUi(self)
        self.webView.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())
        if target[0:4] == 'http':
            self.setWindowTitle('Help')
            self.webView.setUrl(QUrl(target))
        else:
            self.setWindowTitle('Auth')
            self.webView.setHtml(target)
            self.timer = QTimer()
            self.timer.setInterval(500)
            self.timer.timeout.connect(self.codeProbe)
            self.timer.start()
            self.auth_code = None
            self.show()
            self.raise_()

    def codeProbe(self):
        frame = self.webView.page().mainFrame()
        frame.evaluateJavaScript('document.getElementById("code").value')
        codeElement = frame.findFirstElement("#code")
        #val = codeElement.evaluateJavaScript("this.value") # redirect urn:ietf:wg:oauth:2.0:oob
        val = self.webView.title().split('=')
        if val[0] == 'Success code':
            self.auth_code = val[1]
            self.accept()
        else:
            self.auth_code = None

    def patchLoginHint(self,loginHint):
        frame = self.webView.page().mainFrame()
        frame.evaluateJavaScript('document.getElementById("Email").value = "%s"' % loginHint)

    @staticmethod
    def getCode(html,loginHint, title=""):
        dialog = internalBrowser(html)
        dialog.patchLoginHint(loginHint)
        result = dialog.exec_()
        dialog.timer.stop()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.auth_code
        else:
            return None


class QgisODKImportCollectedData(QtWidgets.QDialog, Ui_ImportDialog):

    def __init__(self,module, parent = None): #(self, module, parent = None):
        """Constructor."""
        self.iface = module.iface
        self.module = module
        super(QgisODKImportCollectedData, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

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

    def view(self):
        availableData,response = self.module.getAvailableDataCollections()
        if availableData:
            self.availableDataList.clear()
            self.availableDataList.addItems(availableData)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("Can't download available data %s, %s.") % (response.status_code,response.reason), level=Qgis.Critical, duration=6)
        self.show()
        self.raise_()

    def getRemoteTable(self):
        if self.availableDataList.selectedItems():
            return self.availableDataList.selectedItems()[0].text()
        else:
            return None

    @staticmethod
    def getXFormID(module):
        dialog = QgisODKImportCollectedData(module)
        dialog.view()
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.getRemoteTable()
        else:
            return None


class QgisODKServices(QtWidgets.QDialog, Ui_ServicesDialog):

    services = [
        'ona', 'google_drive', 'odk_aggregate'
    ]
    

    def __init__(self,module, parent = None):
        """Constructor."""
        super(QgisODKServices, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.module = module
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
        self.attachmentsCheckBox.hide()

        
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

    def getExportMethod(self):
        return self.getCurrentService().getExportMethod()

    def getExportExtension(self):
        return self.getCurrentService().getExportExtension()

    def getServiceName(self):
        return self.getCurrentService().getServiceName()

    def setDataSubmissionTable(self,xForm_id):
        submission_url = self.getCurrentService().setDataSubmissionTable(xForm_id)
        return submission_url
        
    def sendForm(self, xForm_id, xForm):
        response = self.getCurrentService().sendForm(xForm_id, xForm)
        return response

    def collectData(self):
        return self.getCurrentService().collectData()

    def getLayerFromTable(self,tableData):
        geojsonDict = self.getCurrentService().getLayerFromTable(tableData)
        return  geojsonDict

    def exportSettings(self):
        settings = {}
        for i in range(0, self.tabServices.count()):
            service_settings = self.tabServices.widget(i).children()[0]
            settings[self.tabServices.tabText(i)] = service_settings.getStructure()
        settings['download_attachments'] = self.attachmentsCheckBox.isChecked()
        return settings

    def importSettings(self,settings):
        for service, params in settings.items():
            for i in range(0, self.tabServices.count()):
                if self.tabServices.tabText(i) == service:
                    service_settings = self.tabServices.widget(i).children()[0]
                    service_settings.applyStructure(params)
        if settings['download_attachments']:
            self.attachmentsCheckBox.setChecked(True)
        else:
            self.attachmentsCheckBox.setChecked(False)


class external_service(QTableWidget):
    
    def __init__(self, parent, parameters):
        super(external_service, self).__init__(parent)
        self.parent = parent
        self.module = parent.parent().parent().parent().module
        self.importDataFromService = QgisODKimportDataFromService(self)
        self.iface = parent.parent().parent().parent().module.iface
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
            if not valueFromSettings or valueFromSettings == "undef":
                self.setItem(row,1,pValue)
                S.setValue("qgisodk/%s/%s/" % (self.service_id,self.item(row,0).text()),parameter[1])
            else:
                self.setItem(row,1,QTableWidgetItem (valueFromSettings))

    def getServiceName(self):
        return self.service_id

    def setup(self):
        S = QSettings()
        S.setValue("qgisodk/", self.parent.parent().currentIndex())
        for row in range (0,self.rowCount()):
            S.setValue("qgisodk/%s/%s/" % (self.service_id,self.item(row,0).text()),self.item(row,1).text())

    def getAuth(self):
        return None

    def getValue(self,key, newValue = None):
        if key == 'download_attachments':
            return self.parent.parent().parent().parent().attachmentsCheckBox.isChecked()
        for row in range (0,self.rowCount()):
            if self.item(row,0).text() == key:
                if newValue:
                    self.item(row, 1).setText(newValue)
                    self.setup() #store to settings
                return self.item(row,1).text()
        raise AttributeError("key not found: " + key)

    def hasValue(self,key):
        for row in range (0,self.rowCount()):
            if self.item(row,0).text() == key:
                return True
        return None

    def guessGeomType(self,geom):
        coordinates = geom.split(';')
        firstCoordinate = coordinates[0].strip().split(' ')
        coordinatesList = []
        if len(firstCoordinate) < 2:
            return "invalid", None
        for coordinate in coordinates:
            decodeCoord = coordinate.strip().split(' ')
            coordinatesList.append([decodeCoord[0],decodeCoord[1]])
        if len(coordinates) == 1:
            return "Point", coordinatesList #geopoint
        if coordinates[-1] == '' and coordinatesList[0][0] == coordinatesList[-2][0] and coordinatesList[0][1] == coordinatesList[-2][1]:
            return "Polygon", coordinatesList #geoshape #geotrace
        else:
            return "LineString", coordinatesList

    def getStructure(self):
        structure = []
        for row in range (0,self.rowCount()):
            structure.append([self.item(row,0).text(),self.item(row,1).text()])
        return structure

    def applyStructure(self,structure):
        for param in structure:
            self.getValue(param[0], newValue=param[1])
        self.setup

    def getLayerFromTable(self, remoteData, ):
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
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

                # build geojson geometry
                jsonCoordinates = []
                for geomCoordinate in geomCoordinates:
                    jsonCoordinates.append([float(geomCoordinate[1]), float(geomCoordinate[0])])
                if geomType == 'Point':
                    feature["geometry"]["coordinates"] = [jsonCoordinates[0][0], jsonCoordinates[0][1]]
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

            # build geojson properties
            for fieldKey, fieldValue in record.items():
                if not fieldKey in ('GEOMETRY',):  # field exclusion
                    feature["properties"][fieldKey] = fieldValue

            geojson["features"].append(feature)

        # metadata = self.getMetadataFromID(self.getValue("data collection table ID"))
        # if metadata:
        #    layerName = metadata['name']
        # else:
        #    layerName = self.tr('collected-data')

        return geojson

class ona(external_service):
    parameters = [
        ["id","ona.io"],
        ["name",""],
        ["project_id", ""],
        ["user", ""],
        ["password", ""],
    ]

    def getAuth(self):
        return requests.auth.HTTPBasicAuth(self.getValue("user"), self.getValue("password"))

    def __init__(self, parent):
        super(ona, self).__init__(parent,self.parameters)

    def getExportMethod(self):
        return 'exportXlsForm'

    def getExportExtension(self):
        return 'xls'
    
    def getAvailableDataCollections(self):
        url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        response = requests.get(url, auth=self.getAuth(), proxies = getProxiesConf())
        if response.status_code != requests.codes.ok:
            return None, response
        forms = response.json()
        availableDataCollections = []
        for form in forms:
            availableDataCollections.append(form["id_string"])
        return availableDataCollections,response
    
    def formIDToPk(self,xForm_id):
        #verify if form exists:
        url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        response = requests.get(url, auth=self.getAuth(), proxies = getProxiesConf())
        if response.status_code != requests.codes.ok:
            return None, response
        forms = response.json()
        form_key = None
        for form in forms:
            if form['sms_id_string'] == xForm_id:
                form_key = form['formid']
                break
        return form_key, response

    def sendForm(self, xForm_id, xForm):
        
        #step1 - verify if form exists:
        form_key, response = self.formIDToPk(xForm_id)
        if response.status_code != requests.codes.ok:
            return response
        if form_key:
            method = 'PATCH'
            url = 'https://api.ona.io/api/v1/forms/%s' % form_key
        else:
            method = 'POST'
            url = 'https://api.ona.io/api/v1/projects/%s/forms' % self.getValue("project_id")
        #step1 - upload form: POST if new PATCH if exixtent
        files = {'xls_file': (xForm, open(xForm, 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}
        response = requests.request(method, url, files=files, auth=self.getAuth(), proxies = getProxiesConf())#, proxies = proxyDict,headers={'Content-Type': 'application/octet-stream'})
        return response

    def getUUIDfield(self):
        return '_uuid'

    def getJSON(self,xForm_id):
        #step1 - verify if form exists:
        form_key, response = self.formIDToPk(xForm_id)
        if response.status_code != requests.codes.ok:
            return response
        if form_key:
            url = 'https://api.ona.io/api/v1/data/%s' % form_key
            response = requests.get(url, auth=self.getAuth(), proxies = getProxiesConf())
            return response

    def setDataSubmissionTable(self,xForm_id):
        return None #defined by ona.io

    def collectData(self):
        '''
        interactive table selection
        '''
        XFormID = QgisODKImportCollectedData.getXFormID(self)
        if XFormID:
            XFormKey, response = self.formIDToPk(XFormID)
            response, remoteTable = self.getTable(XFormKey)
            print ("remoteTable",remoteTable)
            self.importDataFromService.view(XFormID, remoteTable)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"),
                                                self.tr("no data collect table selected"),
                                                level=Qgis.Critical, duration=6)

    def getTable(self,form_key):
        #step1 - verify if form exists:
        #form_key, response = self.formIDToPk(xForm_id)
        #if response.status_code != requests.codes.ok:
        #    self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("error loading csv table %s, %s.") % (
        #    response.status_code, response.reason), level=QgsMessageBar.CRITICAL, duration=6)
        #    return response, None

        if form_key:
            url = 'https://api.ona.io/api/v1/data/%s' % form_key
            response = requests.get(url, auth=self.getAuth(), proxies = getProxiesConf())
            if response.status_code == 200:
                collectData = self.getLayerFromTable(response.json(),excludeGeometryField=False)
                propList = []
                for feature in collectData["features"]:
                    propList.append(feature["properties"])
                return response, propList

            else:
                self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("error loading data table %s, %s.") % (
                response.status_code, response.reason), level=QgsMessageBar.CRITICAL, duration=6)
                return response, None

    def csv_getTable(self,form_key):
        #step1 - verify if form exists:
        #form_key, response = self.formIDToPk(xForm_id)
        #if response.status_code != requests.codes.ok:
        #    self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("error loading csv table %s, %s.") % (
        #    response.status_code, response.reason), level=QgsMessageBar.CRITICAL, duration=6)
        #    return response, None
        def UnicodeDictReader(utf8_data, **kwargs):
            csv_reader = csv.DictReader(utf8_data, **kwargs)#utf_8_encoder(utf8_data)
            for row in csv_reader:
                yield {key:value for key, value in row.items()}
                
        def utf_8_encoder(unicode_csv_data):
            for line in unicode_csv_data:
                yield line.encode('utf-8')
        
        if form_key:
            url = 'https://api.ona.io/api/v1/data/%s.csv' % form_key
            response = requests.get(url, auth=self.getAuth(), proxies = getProxiesConf())
            if response.status_code == 200:
                csvIO = StringIO(response.text)
                csvIn = UnicodeDictReader(csvIO, delimiter=',', quotechar='"')
                csvList = []
                for row in csvIn:
                    remappedRow = {}
                    for key,value in row.items():
                        #print (key,value)
                        #if value[-4:].lower() in ('.png','.jpg','jpeg'):
                        #    img_url = 'https://api.ona.io/api/v1/files/%s?filename=%s/attachments/%s'
                        if '/' in key:
                            cleanedKey = key.split('/')[-1]
                            remappedRow[cleanedKey] = value
                        else:
                            remappedRow[key] = value

                    csvList.append(remappedRow)
                return response, csvList

            else:
                self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("error loading csv table %s, %s.") % (
                response.status_code, response.reason), level=QgsMessageBar.CRITICAL, duration=6)
                return response, None

    def getLayerFromTable(self,remoteData, downloadAttachements = None, excludeGeometryField=True):
        #remoteResponse = self.getJSON(xForm_id)
        #response, remoteData = self.getTable(xForm_id)
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
            print (record)
            #recode attachments:
            attachments = {}
            if '_attachments' in record:
                for attachment in record['_attachments']:
                    fileKey = attachment["download_url"].split('/')[-1]
                    #todo local download attachment files if option is checked
                    attachments[fileKey] = 'https://api.ona.io' + attachment["download_url"]
                    if downloadAttachements and QgsProject.instance().readPath("./") != "./":
                        downloadDir = os.path.join(QgsProject.instance().readPath("./"),'attachments_%s_%s' % (self.getValue("name"),self.getValue("project_id")))
                        if not os.path.exists(downloadDir):
                            os.makedirs(downloadDir)
                        response = requests.get(attachments[fileKey], stream=True, proxies = getProxiesConf())
                        localAttachmentPath = os.path.abspath(os.path.join(downloadDir,fileKey))
                        if response.status_code == 200:
                            with open(localAttachmentPath, 'wb') as f:
                                for chunk in response:
                                    f.write(chunk)
                                attachments[fileKey] = localAttachmentPath
                        else:
                            attachments[fileKey] = ''
            #print ("_attachments",attachments)
            #build geojson properties
            exclusions = ['_attachments','_tags','_notes','_bamboo_dataset_id','_geolocation']
            if excludeGeometryField:
                exclusions.append('GEOMETRY')
            for fieldKey, fieldValue in record.items():
                if not fieldKey in exclusions: # field exclusion to verify
                    if fieldValue in attachments.keys():
                        fieldValue = attachments[fieldValue]
                        
                    if "/" in fieldKey: #check if grouped Field
                        cleanedKey = fieldKey.split("/")[-1]
                    else:
                        cleanedKey = fieldKey
                    fieldRemap = self.module.dlg.treeView.mapNameTofield(cleanedKey) #try to remap field name to existing field using map to property
                    if not fieldRemap:
                        fieldRemap = cleanedKey
                    feature["properties"][fieldRemap] = fieldValue
                    
            geojson["features"].append(feature)

        return geojson

    def downloadMedia(self, URI, downloadDir):
        if URI[:4] != 'http':
            return "image unavailable"
        fileName = URI.split('/')[-1]
        #downloadDir = os.path.join(QgsProject.instance().readPath("./"),'attachments_%s' % layerName)
        if not os.path.exists(downloadDir):
            os.makedirs(downloadDir)
        response = requests.get(URI, allow_redirects=True, stream=True, proxies=getProxiesConf())
        localAttachmentPath = os.path.abspath(os.path.join(downloadDir,fileName))
        if response.status_code == 200:
            with open(localAttachmentPath, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
                return localAttachmentPath
        else:
            print ('error downloading remote file: ',str(response.reason))
            return 'error downloading remote file: ',str(response.reason)


class google_drive(external_service):
    parameters = [
        ["id","google_drive"],
        ["google drive login", ""],
        ["data collectors emails", ""],
        ["folder",""],
        ["data collection table ID", ""],
        ["notifications?(YES/NO)", "YES"]
    ]


    def __init__(self, parent):
        super(google_drive, self).__init__(parent,self.parameters)
        self.authorization = None
        self.verification = None
        self.client_id = "19649210819-f02j5m4hvf9uefejacrs6bclubb57bei.apps.googleusercontent.com" #"88596974458-r5dckj032ton00idb87c4oivqq2k1pks.apps.googleusercontent.com"
        self.client_secret = "vlvv3WCSFHgGvm3D_lQwTtNb" #"c6qKnhBdVxkPMH88lHf285hQ"
        self.getCollectors()

    def collectData(self):
        '''
        interactive table selection
        '''
        #remoteTableName, response = self.getAvailableDataCollections()
        remoteTableName = QgisODKImportCollectedData.getXFormID(self)
        if remoteTableName:
            remoteTableID = self.getIdFromName(remoteTableName)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"),
                                                self.tr("no data collect table selected"),
                                                level=Qgis.Critical, duration=6)
            return

        if remoteTableID != '':
            remoteTable = self.getTable(remoteTableID)
            remoteTableMetadata = self.getMetadataFromID(remoteTableID)
            self.importDataFromService.view(remoteTableMetadata, remoteTable)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"),
                                                self.tr("undefined data collect table ID"),
                                                level=Qgis.Critical, duration=6)

    def getCollectors(self):
        collectorsFromParams = self.getValue("data collectors emails").split(' ')
        self.collectors = []
        email_regex = re.compile(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
        for collector in collectorsFromParams:
            if email_regex.match(collector):
                self.collectors.append(collector)

    def send_message(self, FROM , TO, SUBJECT,  MSG):
        if not self.authorization:
            self.get_authorization()

        # create a message to send
        message = MIMEText(MSG.encode('utf-8'), 'plain', 'utf-8')
        message['to'] = TO
        message['from'] = FROM
        message['subject'] = SUBJECT.encode('utf-8')
        body = {'raw': base64.b64encode(message.as_string())}

        url = 'https://www.googleapis.com/gmail/v1/users/me/messages/send'
        headers = {'Authorization': 'Bearer {}'.format(self.authorization['access_token']), 'Content-Type': 'application/json'}

        response = requests.post(url,headers = headers, data = json.dumps(body), proxies = getProxiesConf(), verify=False)

    def notify(self,XFormName,XFormFolder,collectTableId,collectTableName):
        if self.getValue('notifications?(YES/NO)').upper() == 'YES':
            message = self.tr('''
You are receiving this automatically generated message because you are taking part to a Open Data Kit survey

Your ODK Collect app has to be configured with the following parameters:
a new form called %s has been uploaded in the folder %s shared with you
The Data Collection table is named %s and has the following uri:

https://docs.google.com/spreadsheets/d/%s/edit
            ''') % (XFormName, XFormFolder,collectTableName,collectTableId )
            for email in self.collectors:
                self.send_message(self.getValue('google drive login'),email,'ODK survey notification', message)


    def shareFileWithCollectors(self, id, role = 'reader', type = 'user'):
        self.getCollectors()
        url = 'https://www.googleapis.com/drive/v3/files/%s/permissions' % id
        headers = {'Authorization': 'Bearer {}'.format(self.authorization['access_token']), 'Content-Type': 'application/json'}
        for email in self.collectors:
            metadata = {
                "role": role,
                "type": type,
                "emailAddress": email
            }
            response = requests.post(url, headers=headers, data=json.dumps(metadata), proxies = getProxiesConf(), verify=False)

    def getExportMethod(self):
        return 'exportXForm'

    def getExportExtension(self):
        return 'xml'

    def getIdFromName(self,fileName, mimeType = None):
        if not self.authorization:
            self.get_authorization()
        url = 'https://www.googleapis.com/drive/v3/files'
        headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token'])}
        params = {"q": "name = '%s'" % fileName, "spaces": "drive"}
        response = requests.get( url, headers = headers, params = params, proxies = getProxiesConf(), verify=False )
        if response.status_code == requests.codes.ok:
            found = response.json()
            files = found['files']
            if len(files) > 0:
                if mimeType:
                    if files[0]['mimeType'] == mimeType:
                        return files[0]['id']
                    else:
                        return None
                else:
                    return files[0]['id']
            else:
                return None

    def getMetadataFromID(self,fileID):
        if not self.authorization:
            self.get_authorization()
        url = 'https://www.googleapis.com/drive/v3/files/'+fileID
        headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token'])}
        response = requests.get( url, headers = headers, proxies = getProxiesConf(), verify=False)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            return None


    def getAvailableDataCollections(self):
        if not self.authorization:
            self.get_authorization()

        url = 'https://www.googleapis.com/drive/v3/files'
        headers = {'Authorization':'Bearer {}'.format(self.authorization['access_token'])}
        folderID = self.getIdFromName(self.getValue('folder'), mimeType = 'application/vnd.google-apps.folder')
        params = {"q": "mimeType = 'application/vnd.google-apps.spreadsheet' and '%s' in parents" % folderID, "spaces": "drive"}
        response = requests.get( url, headers = headers, params = params, proxies = getProxiesConf(), verify=False )
        if response.status_code == requests.codes.ok:
            files = response.json()["files"]
            filesList = []
            for file in files:
                filesList.append(file["name"])
            if filesList != []:
                return filesList, response
            else:
                return None, response
        else:
            return None, response



    def createNew(self, name, mimeType, parentsId = None):
        if not self.authorization:
            self.get_authorization()
        if mimeType == 'application/vnd.google-apps.folder' and name == '':
            return 'root'
        foundId = self.getIdFromName(name, mimeType = mimeType)
        if foundId:
            return foundId
        else:
            url = 'https://www.googleapis.com/drive/v3/files'
            headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token']), 'Content-Type': 'application/json'}
            metadata = {
                "name": name,
                "mimeType": mimeType
            }
            if parentsId:
                metadata['parents'] = [parentsId]
            response = requests.post( url, headers = headers, data = json.dumps(metadata), proxies = getProxiesConf(), verify=False)
            if response.status_code != 200 or 'error' in response.json():
                return None
            return response.json()['id']

    def get_verification(self): #phase 1 oauth2
        verification_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob:auto', #
            'scope': 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/gmail.send', #'https://www.googleapis.com/auth/drive.file',
            'login_hint': self.getValue('google drive login')
        }
        response = requests.post('https://accounts.google.com/o/oauth2/v2/auth', params=verification_params, proxies = getProxiesConf(), verify=False)
        if response.status_code == requests.codes.ok:
            self.verification = internalBrowser.getCode(response.text, self.getValue('google drive login'))


    def get_authorization(self): #phase 2 oauth2
        if not self.verification:
            self.get_verification()

        authorization_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': self.verification,
            'grant_type': 'authorization_code',
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob:auto'
        }
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=authorization_params, proxies = getProxiesConf(), verify=False)
        if response.status_code == requests.codes.ok:
            authorization = response.json()
            if 'error' in authorization:
                QMessageBox().warning(None,"Google authorization error", "Google authorization error: %s" % authorization['error'])
                self.verification = None
                self.authorization = None
            else:
                self.authorization = authorization
        elif response.status_code == 401: # token expired
            refresh_params =  {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.authorization['refresh_token'],
                'grant_type': 'refresh_token'
            }

        else:
            pass #print response.reason

    def _getLayer(self,remoteTableName):
        if self.getValue("data collection table ID") == '':
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"),
                                                self.tr("undefined data collect table ID"),
                                                level=Qgis.Critical, duration=6)
            return

        if not self.authorization:
            self.get_authorization()

        metadata = self.getMetadataFromID(self.getValue("data collection table ID"))
        if metadata:
            layerName = metadata['name']
        else:
            layerName = self.tr('collected-data')

        remoteData = self.getTable()
        geojson = self.getLayerFromTable(remoteData)

        if geojson:
            workDir = QgsProject.instance().readPath("./")
            geoJsonFileName = layerName + '_odk-' + time.strftime(
                "%d-%m-%Y") + '.geojson'
            with open(os.path.join(workDir, geoJsonFileName), "w") as geojson_file:
                geojson_file.write(json.dumps(geojson))
            layer = self.iface.addVectorLayer(os.path.join(workDir, layerName), layerName[:-8], "ogr")
            QgsProject.instance().addMapLayer(layer)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"), self.tr("error loading csv table"))


    def getLayerFromTable(self, remoteData, ):
        geojson = {
            "type": "FeatureCollection",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": []
        }

        for record in remoteData:

            '''
            #clean keys
            record={}
            for key,value in raw_record.items():
                record[key.split('-')[-1]] = value
            '''

            if 'GEOMETRY' in record:
                geomType, geomCoordinates = self.guessGeomType(record['GEOMETRY'])
                feature = {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": geomType
                    }
                }

                # build geojson geometry
                jsonCoordinates = []
                for geomCoordinate in geomCoordinates:
                    jsonCoordinates.append([float(geomCoordinate[1]), float(geomCoordinate[0])])
                if geomType == 'Point':
                    feature["geometry"]["coordinates"] = [jsonCoordinates[0][0], jsonCoordinates[0][1]]
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

            # build geojson properties
            for fieldKey, fieldValue in record.items():
                if not fieldKey in ('GEOMETRY',):  # field exclusion
                    feature["properties"][fieldKey] = fieldValue

            geojson["features"].append(feature)
        
        return geojson

    def getTable(self, tableID):
        if not self.authorization:
            self.get_authorization()

        #step1 - verify if form exists:
        url = 'https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s&gid=0' % (tableID,self.getValue("data collection table ID"))
        headers = {'Authorization': 'Bearer {}'.format(self.authorization['access_token']),
                   'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, proxies = getProxiesConf(), verify=False)
        if response.status_code == 200:
            csvIO = StringIO(response.text)
            csvIn = csv.DictReader(csvIO, delimiter=',', quotechar='"')
            csvList = []
            for row in csvIn:
                csvList.append(row)
            geometryField = ''
            for field in csvList[0].keys():
                if field.split('-')[-1] == 'GEOMETRY':
                    geometryField = field
                    prefix = field[:-8]
                    len_prefix = len(field)-8
            print ("geometry field:",geometryField,prefix,len_prefix)
            newCsvList = []
            for row in csvList:
                newRow = {}
                for field in row.keys():
                    newRow[field[len_prefix:]] = row[field] # remap field
                newCsvList.append(newRow)
            return newCsvList
        else:
            pass #print "getTable", response, response.text

    def setDataSubmissionTable(self,xForm_id):
        if not self.authorization:
            self.get_authorization()

        headers = {'Authorization': 'Bearer {}'.format(self.authorization['access_token'])}

        folderId = self.createNew(self.getValue('folder'),'application/vnd.google-apps.folder')
        self.shareFileWithCollectors(folderId, role='reader')

        content_table_id = self.createNew(xForm_id[:-4]+"-collect-table",'application/vnd.google-apps.spreadsheet', parentsId=folderId)
        self.shareFileWithCollectors(content_table_id,role='writer')
        if content_table_id:
            url = 'https://www.googleapis.com/drive/v3/files/'+content_table_id
            response = requests.get(url,headers = headers, proxies = getProxiesConf(), verify=False)
            self.notify(xForm_id,self.getValue('folder'),response.json()['id'],response.json()['name'])
            return 'https://docs.google.com/spreadsheets/d/%s/edit' % response.json()['id']
        else:
            return None
        
    def sendForm(self, xForm_id, xForm):
        if not self.authorization:
            self.get_authorization()

        xForm_id += '.xml'
        fileId = self.getIdFromName(xForm_id)
        
        folderId = self.createNew(self.getValue('folder'),'application/vnd.google-apps.folder')
        self.shareFileWithCollectors(folderId, role='reader')

        metadata = {
            "name": xForm_id,
            "description": 'uploaded by QGISODK plugin'
        }

        if fileId: 
            method = "PATCH"
            url = 'https://www.googleapis.com/upload/drive/v3/files/%s?uploadType=multipart' % fileId
        else:
            method = "POST"
            url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'
            metadata['parents'] = [folderId]
        
        headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token']) }

        data = ('metadata', json.dumps(metadata),'application/json; charset=UTF-8')

        file = (xForm,open(xForm,'r'),'text/xml')
        files = {'data':data, 'file':file }
        response = requests.request(method, url, headers = headers, files = files, proxies = getProxiesConf(), verify=False )
        self.shareFileWithCollectors(response.json()['id'],role='reader')

        return response

    def downloadMedia(self, URL, downloadDir):
        if not os.path.exists(downloadDir):
            os.makedirs(downloadDir)
        headers = {'Authorization': 'Bearer {}'.format(self.authorization['access_token'])}
        response = requests.get(URL, allow_redirects=True, proxies=getProxiesConf(), headers=headers)
        #print (response.headers, response.text)
        if response.status_code == 200:
            d = response.headers['content-disposition']
            fileName = re.findall("filename=(.+)", d)[0].replace('"','')
            localAttachmentPath = os.path.abspath(os.path.join(downloadDir,fileName))
            with open(localAttachmentPath, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
                return localAttachmentPath
        else:
            print ('error downloading remote file: ',str(response.reason))
            return 'error downloading remote file: ',str(response.reason)

class odk_aggregate(external_service):
    """
    (C) 2017 by IIRS - https://github.com/shivareddyiirs
    """

    parameters = [
        ["id", "aggregate"],
        ["url", ''],
        ["user", ''],
        ["password", ''],
    ]

    def __init__(self, parent):
        super(odk_aggregate, self).__init__(parent,self.parameters)
        #self.importDataFromService = QgisODKimportDataFromService(self.module)

    def getAuth(self):
        auth = requests.auth.HTTPDigestAuth(self.getValue('user'),self.getValue('password'))
        #print "auth",auth
        return auth

    def getAvailableDataCollections(self):
        method='GET'
        url=self.getValue('url')+'//formList'
        response= requests.request(method,url,proxies=getProxiesConf(),auth=self.getAuth(),verify=False)
        root=ET.fromstring(response.content)
        keylist=[form.attrib['url'].split('=')[1] for form in root.findall('form')]
        return keylist,response

    def getExportMethod(self):
        return 'exportXForm'

    def getExportExtension(self):
        return 'xml'

    def sendForm(self, xForm_id, xForm):
        #        step1 - verify if form exists:
        formList, response = self.getAvailableDataCollections()
        form_key = xForm_id in formList
        if response.status_code != requests.codes.ok:
            return response
        message = ''
        if form_key:
            message = 'Form Updated'
            method = 'POST'
            url = self.getValue('url') + '//formUpload'
        else:
            message = 'Created new form'
            method = 'POST'
            url = self.getValue('url') + '//formUpload'
        files = open(xForm, 'r')
        files = {'form_def_file': files}
        response = requests.request(method, url, files=files, proxies=getProxiesConf(), auth=self.getAuth(), verify=False)
        if response.status_code == 201:
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"),
                                                self.tr('Layer is online(' + message + '), Collect data from App'),
                                                level=Qgis.Success, duration=6)
        elif response.status_code == 409:
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"),
                                                self.tr("Form exist and can not be updated"),
                                                level=Qgis.Critical, duration=6)
        else:
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"),
                                                self.tr("Form is not sent "),
                                                level=Qgis.Critical, duration=6)
        return response

    def collectData(self):
        '''
        interactive table selection
        '''
        XFormID = QgisODKImportCollectedData.getXFormID(self)
        if XFormID:
            response, remoteTable = self.getTable(XFormID)
            print ("REMOTE TABEL",remoteTable)
            self.importDataFromService.view(XFormID, remoteTable)
        else:
            self.iface.messageBar().pushMessage(self.tr("QGISODK plugin"),
                                                self.tr("no data collect table selected"),
                                                level=Qgis.Critical, duration=6)


    def getTable(self, XFormKey):
        method = 'GET'
        #detect topelement
        url = self.getValue('url')  + '/formXml?formId=' + XFormKey
        response = requests.request(method, url, proxies=getProxiesConf(), auth=self.getAuth(), verify=False)
        root = ET.fromstring(response.content)
        topElement = ''
        for sub_elem in root.iter():
            if sub_elem.get('id'):
                if sub_elem.get('id') == XFormKey:
                    topElement = re.sub("[\{].*?[\}]", "",sub_elem.tag)
        #print "topElement", topElement
        url = self.getValue('url') + '/view/submissionList?formId=' + XFormKey
        table = []
        response = requests.request(method, url, proxies=getProxiesConf(), auth=self.getAuth(), verify=False)
        if not response.status_code == 200:
            return response, table
        #try:
        root = ET.fromstring(response.content)
        ns = '{http://opendatakit.org/submissions}'
        instance_ids = [child.text for child in root[0].findall(ns + 'id')]
        for id in instance_ids:
            if id:
                url = self.getValue(
                    'url') + '/view/downloadSubmission?formId={}[@version=null and @uiVersion=null]/{}[@key={}]'.format(
                    XFormKey,topElement, id)
                response = requests.request(method, url, proxies=getProxiesConf() ,auth=self.getAuth(), verify=False)
                if not response.status_code == 200:
                    return response, table
                root1 = ET.fromstring(response.content)
                data = root1[0].findall(ns + topElement)
                if data:
                    dict = {child.tag.replace(ns, ''): child.text for child in data[0]}
                    dict['UUID'] = id
                    mediaFile = root1.findall(ns + 'mediaFile')
                    if len(mediaFile) > 0:
                        mediaDict = {child.tag.replace(ns, ''): child.text for child in mediaFile[0]}
                        for key, value in dict.items():
                            if value == mediaDict['filename']:
                                dict[key] = mediaDict['downloadUrl']
                    table.append(dict)
        return response, table

    def downloadMedia(self, URI, downloadDir):
        response = requests.get(URI, allow_redirects=True, stream=True, proxies=getProxiesConf(),
                                auth=self.getAuth())
        if response.status_code == 200:
            fileName = re.findall('filename="([^"]*)"', response.headers['content-disposition'])[0]
            #print ("content", fileName,response.headers['content-disposition'], response.status_code)
            localAttachmentPath = os.path.abspath(os.path.join(downloadDir, fileName))
            with open(localAttachmentPath, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            localURI = localAttachmentPath
            try:
                if self.relativePathsCheckBox.isChecked():
                    localURI = os.path.relpath(localURI, QgsProject.instance().readPath("./"))
            except:
                pass
            return localURI
        else:
            return "can't download media: " + str(response.reason)

