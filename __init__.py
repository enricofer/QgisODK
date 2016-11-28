# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisODK
                                 A QGIS plugin
 GeoODK integration for on-filed data collection
                             -------------------
        begin                : 2016-11-15
        copyright            : (C) 2016 by Enrico Ferreguti
        email                : enricofer@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QgisODK class from file QgisODK.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .QgisODK_mod import QgisODK
    return QgisODK(iface)
