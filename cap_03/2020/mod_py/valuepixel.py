#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Value pixel
Description          : Get value of pixel from coordinate map
Date                 : September, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

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
__author__ = 'Luiz Motta'
__date__ = '2020-09-02'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'


import struct

try:
    from osgeo import gdal
except ImportError:
    import gdal

class ValuePixel():
    FMTTYPES = {
        gdal.GDT_Byte: 'B',
        gdal.GDT_Int16: 'h',
        gdal.GDT_UInt16: 'H',
        gdal.GDT_Int32: 'i',
        gdal.GDT_UInt32: 'I',
        gdal.GDT_Float32: 'f',
        gdal.GDT_Float64: 'f'
    }
    def __init__(self, dataset):
        def getBoundBoxImage(transf):
            # (x, y) origin of the (T)op (L)eft pixel
            TL_x, x_res, _x_rotation, TL_y, _y_rotation, y_res = transf
            minX = TL_x
            maxY = TL_y
            maxX = minX + self.ds.RasterXSize * x_res
            minY = maxY + self.ds.RasterYSize * y_res
            return { 'minX': minX, 'maxY': maxY, 'maxX': maxX, 'minY': minY }

        self.ds = dataset
        transf = self.ds.GetGeoTransform()
        self.boundBoxImage = getBoundBoxImage( transf )
        self.transfInv = gdal.InvGeoTransform( transf )
        self.band, self.fmt  = None, None

    def setBand(self, nBand):
        self.band = self.ds.GetRasterBand( nBand )
        fmt = self.FMTTYPES.get( self.band.DataType, 'x')
        self.fmt = fmt

    def __call__(self, x, y):
        px, py = gdal.ApplyGeoTransform( self.transfInv, x, y )
        args = {
            'xoff': int(px), 'yoff': int(py),
            'xsize': 1, 'ysize':1,
            'buf_type': self.band.DataType
        }
        struct_v = self.band.ReadRaster( **args )
        ( value, ) = struct.unpack( self.fmt , struct_v )
        return value
