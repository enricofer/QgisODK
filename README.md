# QgisODK #

The Qgis plugin is aimed to integrate Open Data Kit tools and services in QGis to facilitate on the field data collection.
[Open Data Kit (ODK)](https://opendatakit.org/) is a free and open-source set of tools which help to manage mobile data collection solutions. The typical ODK collection workflow is based on the following activities:

- survey form design (XlsForm/XForm)
- on field data collection by a mobile device [(Google play store)](https://play.google.com/store/apps/details?id=org.odk.collect.android&hl=it)
- data aggregation on server

![](http://programs.goodreturn.org.au/wp-content/uploads/sites/15/2015/05/ODK-Process-New-1024x576.png)

The QgisODK plugin generates forms (XlsForm/XForm) directly from loaded datasources converting the Qgis field Types to Odk Types according to Qgis Field Widget, upload ready to use forms to ODK aggregate server (at the moment the plugin supports ona.io and google drive) and retrieve collected data back to QGis.

Let's follow a QgisODK survey from form creation to data retrieving

## 1 survey design from layer properties ## 

Design layer properties structure editing the forms tab under qgis layer properties. In this tab fields can be added defining their data type. Furthermore each field can be commented to explain the usage and can be associated with a specific "edit widget", the other field properties (alias, WMF, WMS) are not significant for the Qgis ODK plugin.

![](doc/0-qgis-props-fields.png)

Now it's time to switch to QgisODK plugin base dialog called from menu, toolbar or layer context menu

