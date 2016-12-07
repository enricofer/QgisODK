# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisODK
                                 A QGIS plugin
 Qgis / GeoODK integration for on-field data collection
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QMenu, QAction, QIcon, QFileDialog
from PyQt4.QtXml import QDomDocument, QDomElement
from qgis.core import QgsMapLayer, QgsMapLayerRegistry, QgsProject
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources
import json
import xlsxwriter
import requests
import io
import time
# Import the code for the dialog
from QgisODK_mod_dialog import QgisODKDialog, QgisODKServices, QgisODKImportCollectedData
import os.path
from pyxform.builder import create_survey_element_from_dict
from json_form_schema import json_test, dict_test


class QgisODK:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
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

        # Create the dialog (after translation) and keep reference
        self.dlg = QgisODKDialog()
        self.settingsDlg = QgisODKServices()
        self.importCollectedData = QgisODKImportCollectedData(self)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QgisODK')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'QgisODK')
        self.toolbar.setObjectName(u'QgisODK')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QgisODK', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir,"icon.svg") #':/plugins/QgisODK/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QgisODK'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.QODKMenu = QMenu('QgisOKD')
        #self.QODKMenuAction = QAction(QIcon(os.path.join(self.plugin_dir,"icon.svg")), u"QgisODK", self.iface.legendInterface() )
        #self.QODKMenuAction.setMenu(self.QODKMenu)
        self.QODKOutAction = QAction(QIcon(os.path.join(self.plugin_dir,"icon.svg")), self.tr(u"export ODK form"), self.QODKMenu )
        #self.QODKInAction = QAction(QIcon(os.path.join(self.plugin_dir,"icon.svg")), u"ODK in", self.QODKMenu )
        #self.QODKMenu.addAction(self.QODKOutAction)
        #self.QODKMenu.addAction(self.QODKInAction)
        self.iface.legendInterface().addLegendLayerAction(self.QODKOutAction,"","01", QgsMapLayer.VectorLayer,True)
        self.QODKOutAction.triggered.connect(self.contextOdkout)
        #self.QODKInAction.triggered.connect(self.ODKin)
        self.dlg.addGroupButton.clicked.connect(self.addODKGroup)
        self.dlg.exportXFormButton.clicked.connect(self.exportXForm)
        self.dlg.exportXlsFormButton.clicked.connect(self.exportXlsForm)
        self.dlg.cancelButton.clicked.connect(self.closeDlg)
        self.dlg.exportToWebServiceButton.clicked.connect(self.exportToWebService)
        self.dlg.settingsToolButton.clicked.connect(self.openSettings)
        self.dlg.importCollectedDataButton.clicked.connect(self.importCollectedDataAction)
        self.dlg.ODKsaveButton.clicked.connect(self.ODKSaveLayerStateAction)
        self.dlg.ODKloadButton.clicked.connect(self.ODKLoadLayerStateAction)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QgisODK'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        self.iface.legendInterface().removeLegendLayerAction(self.QODKOutAction)

    def openSettings(self):
        self.settingsDlg.show()
        self.settingsDlg.raise_()

    def ODKSaveLayerStateAction(self):
        fieldsState = self.dlg.treeView.backup()
        workDir = QgsProject.instance().readPath("./")
        fileName = QFileDialog().getSaveFileName(None, self.tr("Save QgisODK project"), workDir, "*.json");
        if fileName:
            if QFileInfo(fileName).suffix() != "json":
                fileName += ".json"
            with open(fileName, "w") as json_file:
                json.dump(fieldsState, json_file)

    def ODKLoadLayerStateAction(self):
        workDir = QgsProject.instance().readPath("./")
        fileName = QFileDialog().getOpenFileName(None, self.tr("Load QgisODK project"), workDir, "*.json");
        if fileName:
            with open(fileName, "r") as json_file:
                fieldsState = json.load(json_file)
            ODKProjectName = QFileInfo(fileName).baseName()
            self.dlg.treeView.recover(fieldsState, ODKProjectName)
            self.dlg.setWindowTitle("QgisODK - " + ODKProjectName)
            self.dlg.layersComboBox.setCurrentIndex(0)

    def run(self):
        self.populateVectorLayerCombo()
        self.ODKout(None)
        self.dlg.show()
        self.dlg.raise_()

    def importCollectedDataAction(self):
        self.importCollectedData.show()

    def contextOdkout(self):
        self.populateVectorLayerCombo()
        self.dlg.show()
        self.dlg.raise_()
        current_idx = self.dlg.layersComboBox.findData(self.iface.legendInterface().currentLayer().id())
        if current_idx != -1:
            self.dlg.layersComboBox.setCurrentIndex(current_idx)
        self.ODKout(self.iface.legendInterface().currentLayer())

    def ODKout(self, currentLayer):
        if not currentLayer:
            if self.iface.legendInterface().currentLayer():
                currentLayer = self.iface.legendInterface().currentLayer()
                self.dlg.setWindowTitle("QgisODK - " + currentLayer.name())
            else:
                return
        if currentLayer.type() != QgsMapLayer.VectorLayer:
            return
        currentFormConfig = currentLayer.editFormConfig()
        XMLDocument = QDomDocument("QGISFormConfig")
        XMLFormDef = XMLDocument.createElement("FORM")
        currentFormConfig.writeXml(XMLFormDef)
        XMLDocument.appendChild(XMLFormDef)
        fieldsModel = []
        for i in range(0,len(currentLayer.pendingFields())):
            fieldDef = {}
            fieldDef['fieldName'] = currentLayer.pendingFields()[i].name()
            fieldDef['fieldLabel'] = currentLayer.pendingFields()[i].comment()
            fieldDef['fieldHint'] = ''
            fieldDef['fieldType'] = currentLayer.pendingFields()[i].type()
            fieldDef['fieldEnabled'] = True
            fieldDef['fieldRequired'] = None
            fieldDef['fieldDefault'] = ''
            fieldDef['fieldWidget'] = currentFormConfig.widgetType(i)
            if fieldDef['fieldWidget'] == 'Hidden':
                fieldDef['fieldEnabled'] = None
            else:
                fieldDef['fieldEnabled'] = True
            if fieldDef['fieldWidget'] in ('ValueMap','CheckBox','Photo','FileName'):
                if fieldDef['fieldWidget'] == 'ValueMap':
                    config = {v: k for k, v in currentFormConfig.widgetConfig(i).iteritems()}
                else:
                    config = currentFormConfig.widgetConfig(i)
                fieldDef['fieldChoices'] = config
                #print currentFormConfig.widgetConfig(i)
            else:
                fieldDef['fieldChoices'] = {}
            fieldsModel.append(fieldDef)
        self.dlg.treeView.setFieldModel(currentLayer,fieldsModel)

    def addODKGroup(self):
        self.dlg.treeView.addGroup()
    
    def exportXForm(self, fileName = None):
        workDir = QgsProject.instance().readPath("./")
        if not fileName:
            fileName = QFileDialog().getSaveFileName(None, self.tr("Save XForm"), workDir, "*.xml")
        if QFileInfo(fileName).suffix() != "xml":
            fileName += ".xml"
        json_out = self.dlg.treeView.renderToDict()
        survey = create_survey_element_from_dict(json_out)
        warnings = []
        xform = survey.to_xml(validate=None, warnings=warnings)
        with io.open(fileName, "w", encoding="utf8") as xml_file:
            xml_file.write(xform)
        xForm_id = json_out["name"]
        return xForm_id
    
    def exportXlsForm(self, fileName = None):
        workDir = QgsProject.instance().readPath("./")
        if not fileName:
            fileName = QFileDialog().getSaveFileName(None, self.tr("Save XlsForm"), workDir, "*.xls")
        if QFileInfo(fileName).suffix() != "xls":
            fileName += ".xls"
        tableDef = self.dlg.treeView.renderToTable()
        workbook = xlsxwriter.Workbook(fileName)
        for sheetName, sheetContent in tableDef.iteritems():
            worksheet = workbook.add_worksheet(sheetName)
            for row, rowContent in enumerate(sheetContent):
                for col, cellContent in enumerate(rowContent):
                    worksheet.write(row, col,cellContent)
        workbook.close()
        with open(fileName, mode='rb') as f:
            fileContent = f.read()
        xForm_id = tableDef['settings'][1][1]
        return xForm_id

    def exportToWebService(self):
        tmpXlsFileName = os.path.join(self.plugin_dir,"tmpodk."+self.settingsDlg.getExportExtension())
        exportMethod = getattr(self, self.settingsDlg.getExportMethod())
        xForm_id = exportMethod(fileName=tmpXlsFileName)
        response = self.settingsDlg.sendForm(xForm_id,tmpXlsFileName)
        os.remove(tmpXlsFileName)
        if not response.status_code in (200,201):
            #msg = self.iface.messageBar().createMessage( u"QgisODK plugin error saving form %s, %s." % (response.status_code,response.reason))
            #self.iface.messageBar().pushWidget(msg,QgsMessageBar.WARNING, 6)
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("error saving form %s, %s.") % (response.status_code,response.reason), level=QgsMessageBar.CRITICAL, duration=6)
        else:
            #msg = self.iface.messageBar().createMessage( u"QgisODK plugin: form successfully exported")
            #self.iface.messageBar().pushWidget(msg,QgsMessageBar.INFO, 6)
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("form successfully exported"), level=QgsMessageBar.INFO, duration=6)

    
    def closeDlg(self):
        self.dlg.close()

    
    
    def populateVectorLayerCombo(self):
        try:
            self.dlg.layersComboBox.currentIndexChanged.disconnect(self.VectorLayerComboChanged)
        except:
            pass
        self.dlg.layersComboBox.clear()
        self.dlg.layersComboBox.addItem("",None)
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                self.dlg.layersComboBox.addItem(layer.name(),layer.id())
        if self.iface.legendInterface().currentLayer():
            current_idx = self.dlg.layersComboBox.findData(self.iface.legendInterface().currentLayer().id())
            if current_idx != -1:
                self.dlg.layersComboBox.setCurrentIndex(current_idx)
        self.dlg.layersComboBox.currentIndexChanged.connect(self.VectorLayerComboChanged)

    def VectorLayerComboChanged(self,idx):
        if self.dlg.layersComboBox.itemData(idx):
            layer = QgsMapLayerRegistry.instance().mapLayer(self.dlg.layersComboBox.itemData(idx))
            self.ODKout(layer)

    #method to get xml definition of layer state
    def getDomDef(self,layer):
        XMLDocument = QDomDocument("undo-layer")
        XMLMapLayers = QDomElement()
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = QDomElement()
        XMLMapLayer = XMLDocument.createElement("maplayer")
        layer.writeLayerXML(XMLMapLayer,XMLDocument)
        XMLMapLayers.appendChild( XMLMapLayer )
        XMLDocument.appendChild( XMLMapLayers )
        return XMLMapLayer

    def ODKin(self):#,sheetId):
        geojsonDict,response = self.settingsDlg.getLayer(self.iface.legendInterface().currentLayer().name())
        if geojsonDict and response.status_code == requests.codes.ok:
            workDir = QgsProject.instance().readPath("./")
            geoJsonFileName = self.iface.legendInterface().currentLayer().name()+'_odk-'+time.strftime("%d-%m-%Y")+'.geojson'
            with open(os.path.join(workDir,geoJsonFileName), "w") as geojson_file:
                geojson_file.write(json.dumps(geojsonDict))
            layer = self.iface.addVectorLayer(os.path.join(workDir,geoJsonFileName), geoJsonFileName[:-8], "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            currentLayerState = self.getDomDef(self.iface.legendInterface().currentLayer())
                
            currentFormConfig = currentLayer.editFormConfig() #recover
            fieldsModel = {}
            for i in range(0,len(currentLayer.pendingFields())):
                fieldsModel[currentLayer.pendingFields()[i].name()] = currentFormConfig.widgetType(i)
                
            layer.readLayerXML(currentLayerState)
        else:
            print response.text
            #msg = self.iface.messageBar().createMessage( u"QgisODK plugin error loading csv table %s, %s." % (response.status_code,response.reason))
            #self.iface.messageBar().pushWidget(msg,QgsMessageBar.WARNING, 6)
            self.iface.messageBar().pushMessage(self.tr("QgisODK plugin"), self.tr("error loading csv table %s, %s.") % (response.status_code,response.reason), level=QgsMessageBar.CRITICAL, duration=6)

