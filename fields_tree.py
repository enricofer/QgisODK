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

from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QLineEdit, QComboBox, QCheckBox, QAbstractItemView
from PyQt4.QtGui import QTreeView, QStandardItem, QStandardItemModel, QItemSelectionModel, QItemDelegate
from PyQt4.QtGui import QPen, QBrush, QColor

from qgis.core import QGis

import json
import unicodedata
import re

appearanceDef = {
    'group': ['field-list','table-list'],
    'select one': ['field-list','table-list','minimal','label','list-nolabel','autocomplete','autocomplete_chars','horizontal','compact-2','quick'],
    'select multiple': ['field-list','table-list','minimal','label','list-nolabel','autocomplete','autocomplete_chars','horizontal','compact-2','quick'],
    'date': ['default','no-calendar','month-year','year'],
    'image': ['default','annotate','draw','signature'],
    'geopoint': ['default','maps','placement-map'],
    'geotrace': ['default','maps','placement-map'],
    'geoshape': ['default','maps','placement-map'],
}

def slugify (s):
    if type(s) is unicode:
        slug = unicodedata.normalize('NFKD', s)
    elif type(s) is str:
        slug = s
    else:
        raise AttributeError("Can't slugify string")
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug=re.sub(r'--+',r'-',slug)
    return slug

class ODK_fields(QTreeView):

    def __init__(self, parent):
        super(ODK_fields, self).__init__(parent = parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop) #QAbstractItemView.InternalMove
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(True)
        self.showDropIndicator()
        self.setItemDelegate(ODKDelegate(self))
        self.setIndentation(15)
        self.setRootIsDecorated(True)


    def setFieldModel(self,layer,fieldsModel):
        self.layerName = layer.name()
        if layer.geometryType() == QGis.Point:
            self.geometry = 'geopoint'
        elif layer.geometryType() == QGis.Line:
            self.geometry = 'geotrace'
        elif layer.geometryType() == QGis.Polygon:
            self.geometry = 'geoshape'
        else :
            self.geometry = None
        
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['enabled', 'label', 'ODK type', 'hint', 'required', 'default', 'QVar_type', 'widget', 'choices','appearance'])
        
        if self.geometry:
            geo_field = {
                'fieldEnabled': True,
                'fieldName':'GEOMETRY',
                'fieldLabel':'Insert geometry',
                'fieldType': self.geometry,
                'fieldHint': '',
                'fieldRequired': True,
                'fieldDefault': '',
                'fieldQtype':'',
                'fieldWidget':'',
                'fieldChoices':{}
            }
            fieldsModel.insert(0,geo_field)

        metadata = [
            ['start','start','Start date and time of the survey',''],
            ['end','end','End date and time of the survey',''],
            ['today','today','Day of the survey',''],
            ['deviceid','deviceid','IMEI (International Mobile Equipment Identity)',''],
            ['subscriberid','subscriberid','IMSI (International Mobile Subscriber Identity)',''],
            ['simserial','simserial','SIM serial number',''],
            ['phonenumber','phonenumber','Phone number (if available)',''],
            #['instanceID','text','instance unique identifier','${uuid()}'],
        ]
        for count,field in enumerate (fieldsModel):
            name_item = fieldItem(field['fieldName'])
            name_item.setFlags(Qt.ItemIsSelectable)
            name_item.setEnabled(True)
            name_item.setDragEnabled(True)
            name_item.addFieldDef(field)
            model.appendRow(name_item)
            
        self.setModel(model)
        self.hideColumn(6)
        self.hideColumn(7)
        self.hideColumn(8)

        metadata_group = self.addGroup(metadata = True)
        for m in metadata:
            metadata_field = {
                'fieldEnabled': None,
                'fieldName':m[0],
                'fieldLabel': '',
                'fieldType': m[1],
                'fieldHint': m[2],
                'fieldRequired': '',
                'fieldDefault': m[3],
                'fieldQtype':'',
                'fieldWidget': '',
                'fieldChoices':{}
            }
            metadata_item = fieldItem(metadata_field['fieldName'])
            metadata_item.setFlags(Qt.ItemIsSelectable)
            metadata_item.setEnabled(True)
            metadata_item.setDragEnabled(True)
            metadata_item.addFieldDef(metadata_field)
            metadata_group.appendRow(metadata_item)

        self.setUniformRowHeights(True)
        self.expandAll()
        self.collapse(metadata_group.index())

    def addGroup(self, name = None, metadata = None):
        model = self.model()
        group_item = QStandardItem(name or 'New Group')
        group_item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable)
        group_item.setEnabled(True)
        if metadata:
            group_item.setText('Metadata')
        group_item.setDropEnabled(True)
        group_item.setDragEnabled(True)
        group_item.setCheckable(True)
        group_item.setCheckState(Qt.Checked)
        group_row = [group_item]
        for i in range (1,8):
            null_item = QStandardItem('')
            null_item.setEnabled(False)
            null_item.setDropEnabled(True)
            null_item.setDragEnabled(False)
            #group_row.append(null_item)
        model.appendRow(group_row)
        if not name:
            self.setCurrentIndex(model.indexFromItem(group_item))
        return group_item


    def renderToTable(self, title=None):
        if not title:
            title = self.layerName
        model = self.model()
        self.tableDefault()
        for count in range (0, model.rowCount()):
            childRow = model.item(count)
            if childRow.rowCount() > 0 and childRow.checkState() == Qt.Checked: #exclude void groups and not enabled
                probeSubChildRow = model.data(model.index(0,2,childRow.index()),Qt.DisplayRole)
                print "PROBE",probeSubChildRow
                if probeSubChildRow: #is fieldItem
                    self.renderItemStructure(childRow.index(), output = 'table')
                else: #is groupItem
                    self.renderGroupStructure(childRow.index(), output = 'table')
        self.tableDef['settings'].append([title,slugify(title)])
        return self.tableDef


    def renderToDict(self,title = None):
    
        if not title:
            title = self.layerName
        model = self.model()
        childrenList = []
        for count in range (0, model.rowCount()):
            childRow = model.item(count)
            if childRow.rowCount() > 0 and childRow.checkState() == Qt.Checked: #exclude void groups and not enabled
                probeSubChildRow = model.data(model.index(0,2,childRow.index()),Qt.DisplayRole)
                print "PROBE",probeSubChildRow
                if probeSubChildRow: #is fieldItem
                    dict = self.renderItemStructure(childRow.index(), output = 'dict')
                else: #is groupItem
                    dict = self.renderGroupStructure(childRow.index(), output = 'dict')
                if dict:
                    childrenList.append(dict)
                    
        if childrenList == []:
            return None
        else:
            return {
           "name":slugify(title),
           "title":title,
           "sms_keyword":slugify(title),
           "default_language":"default",
           "id_string":slugify(title),
           "type":"survey",
           "children":childrenList
        }

    def tableDefault(self):
        self.tableDef = {
            "survey":[['type','name','label','hint','constraint','constraint_message','required','appearance','default','relevant','read_only','calculation']],
            "choices":[['list_name','name','label']],
            "settings":[['form_title','form_id']]
        }

    def renderItemStructure(self,itemIndex, output = 'dict'):
        '''
        procedure to build standard item dict
        '''
        model = self.model()
        defOrder = ['fieldName', 'fieldLabel', 'fieldType', 'fieldHint', 'fieldRequired', 'fieldDefault', 'fieldQtype', 'fieldWidget', 'fieldChoices','fieldAppearance']
        fieldDefFromModel = {}
        for count in range (0,len(defOrder)):
            if count == 0:
                fieldDefFromModel['fieldName'] = itemIndex.data(Qt.DisplayRole)
                print "FIELD:",fieldDefFromModel['fieldName']
            else:
                fieldInd = model.index(0,count,itemIndex)
                if defOrder[count] == 'fieldRequired':
                    if self.model().itemFromIndex(fieldInd).checkState() == Qt.Checked:
                        fieldDefFromModel['fieldRequired'] = True
                    else:
                        fieldDefFromModel['fieldRequired'] = None
                else:
                    fieldDefFromModel[defOrder[count]] = fieldInd.data(Qt.DisplayRole)
        
        if not fieldDefFromModel['fieldType']:
            return None
        if output == 'dict':
            structure = {
                "type":  fieldDefFromModel['fieldType'],
                "name":  fieldDefFromModel['fieldName'],
                "label": fieldDefFromModel['fieldLabel'] or fieldDefFromModel['fieldName']
            }

            if fieldDefFromModel['fieldHint']:
                structure["hint"] = fieldDefFromModel['fieldHint']

            if fieldDefFromModel['fieldDefault']:
                structure["default"] = fieldDefFromModel['fieldDefault']

            if fieldDefFromModel['fieldRequired']:
                structure["bind"] = {"required": "yes"}
            
            if not fieldDefFromModel['fieldAppearance'] in ['default','']:
                structure["control"] = {"appearance": fieldDefFromModel['fieldAppearance']}

            if fieldDefFromModel['fieldChoices'] != {} and fieldDefFromModel['fieldType'] in ['select one','select multiple']:
                choicesList = []
                choicesDict = json.loads(fieldDefFromModel['fieldChoices'])
                for name, label in choicesDict.iteritems():
                    choicesList.append({"name": name, "label": label})
                structure["choices"] = choicesList
            return structure
        elif output == 'table':
            surveyRow = [None] * 12
            surveyRow[0] = fieldDefFromModel['fieldType']
            surveyRow[1] = fieldDefFromModel['fieldName']
            surveyRow[2] = fieldDefFromModel['fieldLabel'] or fieldDefFromModel['fieldName']
            surveyRow[3] = fieldDefFromModel['fieldHint']
            surveyRow[7] = fieldDefFromModel['fieldAppearance']
            if fieldDefFromModel['fieldRequired']:
                 surveyRow[6] = 'yes'
            if fieldDefFromModel['fieldChoices'] != {} and fieldDefFromModel['fieldType'] in ['select one',
                                                                                              'select multiple']:
                surveyRow[0] = surveyRow[0] + ' ' + slugify(fieldDefFromModel['fieldName'])
                choicesDict = json.loads(fieldDefFromModel['fieldChoices'])
                for name, label in choicesDict.iteritems():
                    self.tableDef['choices'].append([slugify(fieldDefFromModel['fieldName']),name,label])
            self.tableDef['survey'].append(surveyRow)


    def renderGroupStructure(self,groupIndex, output = 'dict'):
        model = self.model()
        groupLabel = model.itemFromIndex(groupIndex).data(Qt.DisplayRole)
        groupName = slugify(groupLabel)
        if model.itemFromIndex(groupIndex).rowCount() == 0:
            return None
        childrenList = []
        if groupName != 'metadata' and output == 'table':
            self.tableDef['survey'].append(['begin group',groupName,groupLabel,None,None,None,None,"field-list",None,None,None,None])
        for count in range (0, model.itemFromIndex(groupIndex).rowCount()):
            childRow = model.itemFromIndex(groupIndex.child(count,0))
            childrenList.append(self.renderItemStructure(childRow.index(), output = output))
        if groupName != 'metadata' and output == 'table':
            self.tableDef['survey'].append(['end group',groupName,None,None,None,None,None,None,None,None,None,None])
        if childrenList == []:
            return None
        else:
            if output == 'dict':
                return {"control": {"appearance": "field-list"}, "type": "group", "name": groupName, "label": groupLabel,
                       "children": childrenList}


class ODKDelegate(QItemDelegate):
    '''
    def __init__(self, parent, parentClass):
        QItemDelegate.__init__(self, parent)
        self.parentClass = parentClass
    '''

    def createEditor (self, parent, option, index):
        try:
            content = index.model().data(index, Qt.EditRole)
            if content == None:
                return None
        except:
            return None
        column = index.column()
        row = index.row()
        parentNode = index.model().data(index.parent(), Qt.EditRole)
        
        print column,row, parentNode
        if column == 2 and parentNode: # combobox for odk types
            editorQWidget = QComboBox(parent)
            #QVariantType = indexQModelIndex.model().item(row,6).data()
            if content in ['text','note','image','barcode','audio','video']:
                combobox_items = ['text','note','image','barcode','audio','video']
            elif content in ['date', 'datetime']:
                combobox_items = ['date', 'time', 'datetime']
            elif content in ['geopoint','geoshape','geotrace']:
                combobox_items = ['geopoint','geoshape','geotrace']
            else:
                combobox_items = [content]
            editorQWidget.addItems(combobox_items)
            editorQWidget.setCurrentIndex(editorQWidget.findText(content))
            return editorQWidget
        elif column == 9 and parentNode: # combobox for appearance
            contentType = index.model().data(index.sibling(0,2), Qt.DisplayRole)
            print "contentType", contentType
            if contentType == '':
                return
            editorQWidget = QComboBox(parent)
            editorQWidget.addItems(appearanceDef[contentType])
            #editorQWidget.setCurrentIndex(0)
            return editorQWidget
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    def expaint(self, painter, option, index):
        painter.save()
        content = index.model().data(index, Qt.EditRole)
        column = index.column()
        row = index.row()
        parentNode = index.model().data(index.parent(), Qt.EditRole)
        if parentNode:
            painter.fillRect(option.rect, QBrush(QColor(200, 200, 200)))
        painter.setPen(QPen(Qt.black))
        painter.drawText(option.rect, Qt.AlignLeft, content)
        painter.restore()


class fieldItem(QStandardItem):

    def addFieldDef(self,fieldDef):
        self.fieldDef = fieldDef
        self.defOrder = ['fieldName', 'fieldLabel', 'fieldType', 'fieldHint', 'fieldRequired', 'fieldDefault', 'fieldQtype', 'fieldWidget', 'fieldChoices','fieldAppearance']
        fieldDef['fieldType'] = self.getODKType(fieldDef)
        if fieldDef['fieldType'] in appearanceDef.keys():
            fieldDef['fieldAppearance'] = appearanceDef[fieldDef['fieldType']][0]
        else:
            fieldDef['fieldAppearance'] = 'default'
        row = []
        print fieldDef
        for fdef in self.defOrder:
            if fdef == 'fieldName':
                sub_item = QStandardItem(None)
            elif fdef == 'fieldRequired':
                sub_item = QStandardItem(None)
                sub_item.setCheckable(True)
                if fieldDef['fieldRequired']:
                    sub_item.setCheckState(Qt.Checked)
                else:
                    sub_item.setCheckState(Qt.Unchecked)
            elif fdef == 'fieldChoices':
                sub_item = QStandardItem(json.dumps(fieldDef[fdef]))
            else:
                sub_item = QStandardItem(str(fieldDef[fdef]) or '')
            sub_item.setDropEnabled(False)
            sub_item.setDragEnabled(False)
            row.append(sub_item)
        self.appendRow(row)
        self.setCheckable(True)
        if fieldDef['fieldEnabled']:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)


    def getODKType(self,field):
        if field['fieldType'] in ['geopoint','geoshape','geotrace','start', 'end', 'today', 'deviceid', 'subscriberid', 'simserial', 'phonenumber']:
            field['fieldQtype'] = "UserType"
            return field['fieldType']
        field['fieldQtype'] = QVariant.typeToName(field['fieldType'])
        if field['fieldWidget'] == "ValueMap": # First try to decode Qgis form widgets
            itemType = 'select one'
        elif field['fieldWidget'] == "CheckBox":
            itemType = 'select one'
            field['fieldChoices'] = {str(field['fieldChoices']['CheckedState']):"No",str(field['fieldChoices']['UncheckedState']):"Yes"}
        elif field['fieldWidget'] == "Photo":
            itemType = 'image'
        else: #decoding QVariant type of field
            if field['fieldType'] in [2,3,4,32,33,35,36]:
                itemType = 'integer'
            elif field['fieldQtype'] == 'QString':
                itemType = 'text'
            elif field['fieldQtype'] == 'QDate':
                itemType = 'datetime'
            elif field['fieldType'] in [6,38]:
                itemType = 'decimal'
            else:
                raise AttributeError("Can't cast QVariant to ODKType: " + field['fieldType'])
        return itemType


