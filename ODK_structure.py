# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisODK
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

import unicodedata

def slugify (s):
    slug = unicodedata.normalize('NFKD', s)
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug=re.sub(r'--+',r'-',slug)

class ODKmodel:

    def __init__(self,title):
        self.structure = self.getBaseStructure(title)

    def getBaseStructure (self,title):

        return {
           "name":title + "_xlsform",
           "title":title,
           "sms_keyword":slugify(title),
           "default_language":"default",
           "id_string":slugify(title),
           "type":"survey",
           "children":[]
        }

class ODKnode:

    def __init(self, name, label):
        self.name = name
        self.value = label

    def render


class ODKitem:

    def __init(self,name, label,type, hint = None, required = None, default = None, choices = None):
        self.name = name
        self.value = label
        self.type = type
        self.required = required
        self.default = default
        self.choices = choices
        if not type in ['integer','text','decimal','geopoint','geoshape','image','barcode','date','datetime','audio','video']:
            self.error = 'ODKitem type not defined'
            raise AttributeError(self.error)
        else:
            self.error = None


    def getTypeFromValue(self,value):

        if type(value) is int or type(itemValue) is long:
            itemType = 'integer'
        elif type(value) is string or type(itemValue) is unicode:
            itemType = 'text'
        elif type(value) is float:
            itemType = 'decimal'
        else raise AttributeError('getItemStructure type not defined')
        return itemType

    def renderItemStructure (self,fieldDef):
        '''
        procedure to build standard item dict
        '''


        structure = {
            "type": fieldDef.type,
            "name": fieldDef.name,
            "label": fieldDef.label
        }

        if fieldDef.hint:
            structure["hint"] = self.hint

        if fieldDef.default:
            structure["default"] = self.default

        if fieldDef.required:
            structure["bind"] = {"required":"yes"}

        if fieldDef.choices:
            choicesList = []
            for name, label in self.choices.iteritems()
                choicesList.append({"name":name, "label":label})
            structure["choices"] = choicesList

        return structure


    def groupItems(self,groupName, groupLabel, items):

        groupStruct = {"control":{"appearance":"field-list"},"type":"group","name":groupName,"label":groupLabel,"children":[]}
        for item in items:
            renderItemStructure["children"].append(renderItemStructure(item))

        return groupStruct
