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
import webbrowser

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QTableWidget, QWidget, QTableWidgetItem, QSizePolicy, QMessageBox
from PyQt4.QtCore import Qt, QSettings, QSize, QSettings, QTranslator, qVersion, QCoreApplication, QTimer
from qgis.core import QgsProject, QgsMapLayerRegistry, QgsNetworkAccessManager
from qgis.gui import QgsMessageBar

from QgisODK_mod_dialog_base import Ui_QgisODKDialogBase
from QgisODK_mod_dialog_services import Ui_ServicesDialog
from QgisODK_mod_dialog_import import Ui_ImportDialog
from QgisODK_mod_dialog_choices import Ui_ChoicesDialog
from QgisODK_mod_dialog_browser import Ui_AuthBrowser

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


    

class authBrowser(QtGui.QDialog, Ui_AuthBrowser):

    def __init__(self, html, parent = None):
        super(authBrowser, self).__init__(parent)
        self.setupUi(self)
        self.webView.setHtml(html)
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.codeProbe)
        self.timer.start()
        self.show()
        self.raise_()
        self.auth_code = None
        #self.webView.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())

    def codeProbe(self):
        frame = self.webView.page().mainFrame()
        frame.evaluateJavaScript('document.getElementById("code").value')
        codeElement = frame.findFirstElement("#code")
        #val = codeElement.evaluateJavaScript("this.value") # redirect urn:ietf:wg:oauth:2.0:oob
        val = self.webView.title().split('=')
        if val[0] == 'Success code':
            self.auth_code = val[1]
            print self.auth_code
            self.accept()
        else:
            self.auth_code = None

    @staticmethod
    def getCode(html, title=""):
        dialog = authBrowser(html)
        result = dialog.exec_()
        dialog.timer.stop()
        if result == QtGui.QDialog.Accepted:
            return dialog.auth_code
        else:
            return None


class QgisODKImportCollectedData(QtGui.QDialog, Ui_ImportDialog):

    def __init__(self, module, parent = None):
        """Constructor."""
        self.iface = module.iface
        self.settingsDlg = module.settingsDlg
        super(QgisODKImportCollectedData, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

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

    def show(self):
        availableData,response = self.settingsDlg.getAvailableDataCollections()
        if availableData:
            self.availableDataList.clear()
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
        else:
            print response.text
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("error loading csv table %s, %s.") % (response.status_code,response.reason), level=QgsMessageBar.CRITICAL, duration=6)

        
    def reject(self):
        self.hide()

class QgisODKServices(QtGui.QDialog, Ui_ServicesDialog):

    services = [
        'ona', 'google_drive'
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

    def getExportMethod(self):
        return self.getCurrentService().getExportMethod()

    def getExportExtension(self):
        return self.getCurrentService().getExportExtension()

    def getServiceName(self):
        return self.getCurrentService().getServiceName()
        
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


    def getServiceName(self):
        return self.service_id


    def setup(self):
        S = QSettings()
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
            availableDataCollections.append(form["id_string"])
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

    def getExportMethod(self):
        return 'exportXlsForm'

    def getExportExtension(self):
        return 'xls'

    def sendForm(self, xForm_id, xForm):
        
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

class google_drive(external_service):
    parameters = [
        ["id","google_drive"],
        ["folder",""],
        ["google drive login", ""],
        ["google sheet upload", ""]
    ]
    
    def __init__(self, parent):
        super(google_drive, self).__init__(parent,self.parameters)
        self.authorization = None
        self.verification = None
        self.client_id = "88596974458-r5dckj032ton00idb87c4oivqq2k1pks.apps.googleusercontent.com"
        self.client_secret = "c6qKnhBdVxkPMH88lHf285hQ"

    def getExportMethod(self):
        return 'exportXForm'

    def getExportExtension(self):
        return 'xml'

    def getIdFromName(self,fileName, mimeType = None):
        if not self.authorization:
            self.get_authorization()
        url = 'https://www.googleapis.com/drive/v3/files'
        headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token'])}
        params = {"q": "name contains '%s'" % fileName, "spaces": "drive"}
        response = requests.get( url, headers = headers, params = params )
        print "getIdFromName", response
        print "getIdFromName", response.json()
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
        

    def createFolder(self,folderName):
        if not self.authorization:
            self.get_authorization()
        if folderName == '':
            return 'root'
        folderId = self.getIdFromName(folderName, mimeType = 'application/vnd.google-apps.folder')
        print "FOLDER:", folderName, folderId
        if folderId:
            print "trovato"
            return folderId
        else:
            url = 'https://www.googleapis.com/drive/v3/files'
            headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token']), 'Content-Type': 'application/json'}
            metadata = {
                "name": folderName,
                "mimeType": 'application/vnd.google-apps.folder'
            }
            response = requests.post( url, headers = headers, data = json.dumps(metadata))
            print "CREATE FOLDER",response.json()
            print response.json()
            return response.json()['mimeType']

    def get_verification(self): #phase 1 oauth2
        verification_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob:auto', #
            'scope': 'https://www.googleapis.com/auth/drive', #'https://www.googleapis.com/auth/drive.file',
            'login_hint': self.getValue('google drive login')
        }
        response = requests.post('https://accounts.google.com/o/oauth2/v2/auth', params=verification_params)
        if response.status_code == requests.codes.ok:
            self.verification = authBrowser.getCode(response.text)
            print "verificated"
        
        
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
        print authorization_params
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=authorization_params)
        print response.json()
        if response.status_code == requests.codes.ok:
            authorization = response.json()
            print "ok"
            if 'error' in authorization:
                QMessageBox().warning(None,"Google authorization error", "Google authorization error: %s" % authorization['error'])
                self.verification = None
                self.authorization = None
            else:
                print "authorized"
                self.authorization = authorization
        elif response.status_code == 401: # token expired
            print "expired"
            refresh_params =  {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.authorization['refresh_token'],
                'grant_type': 'refresh_token'
            }

        else:
            print response.text
        
        
    def sendForm(self, xForm_id, xForm):
        if not self.authorization:
            self.get_authorization()

        xForm_id += '.xml'
        fileId = self.getIdFromName(xForm_id)
        
        folderId = self.createFolder(self.getValue('folder'))

        metadata = {
            "name": xForm_id,
            "description": 'uploaded by QgisODK plugin'
        }

        if fileId: 
            method = "PATCH"
            url = 'https://www.googleapis.com/upload/drive/v3/files/%s?uploadType=multipart' % fileId
            print "UPDATE", xForm_id
        else:
            method = "POST"
            url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'
            metadata['parents'] = [folderId]
            print "CREATE", xForm_id
        
        headers = { 'Authorization':'Bearer {}'.format(self.authorization['access_token']) }

        #data = ('metadata',json.dumps(DataDict(name = xForm_id, description = 'uploaded by QgisODK plugin', parents = [folderId])),'application/json; charset=UTF-8')
        data = ('metadata', json.dumps(metadata),'application/json; charset=UTF-8')

        file = (xForm,open(xForm,'r'),'text/xml')
        files = {'data':data, 'file':file }
        response = requests.request(method, url, headers = headers, files = files )
        
        #print response.json()
        
        return response
        
        
class DataDict(dict):
  def read(self):
      return str( self )