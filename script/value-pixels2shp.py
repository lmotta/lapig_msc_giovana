#!/usr/bin/python3
# # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Value pixels to shapefile
Description          : Add values image's pixel of point inside shapefile 
Date                 : September, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

 ***************************************************************************/

Dependences:
- mod_py.valuepixel

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys
import struct
import argparse

try:
    from osgeo import ogr, osr, gdal
except ImportError:
    import ogr, osr, gdal
gdal.UseExceptions()

from mod_py.valuepixel import ValuePixel


class LayerValuePixels():
    TYPEBAND2FIELD = {
        gdal.GDT_Byte: ogr.OFTInteger,
        gdal.GDT_UInt16: ogr.OFTInteger,
        gdal.GDT_Int16: ogr.OFTInteger,
        gdal.GDT_UInt32: ogr.OFTInteger64,
        gdal.GDT_Int32: ogr.OFTInteger64,
        gdal.GDT_Float32: ogr.OFTReal
    }

    @staticmethod
    def getLayerPoint(pathfile, fieldName, updateField):
        if not os.path.isfile( pathfile ):
            msg = f"Missing file '{pathfile}'"
            return { 'isOk': False, 'message': msg }
        ds = ogr.Open( pathfile, 1 )
        if ds is None:
            msg = f"Error read Point Layer '{pathfile}'"
            return { 'isOk': False, 'message': msg }
        layer = ds.GetLayer()
        if layer is None:
            ds = None
            msg = f"Error read Point Layer '{pathfile}'"
            return { 'isOk': False, 'message': msg }
        if layer.GetSpatialRef() is None:
            ds = None
            msg = f"Error Point Layer '{pathfile}' missing Spatial Reference"
            return { 'isOk': False, 'message': msg }
        if not layer.GetGeomType() == ogr.wkbPoint:
            msg = f"Geometry type of Point Layer '{pathfile}' need be a POINT"
            return { 'isOk': False, 'message': msg }
        defn = layer.GetLayerDefn()
        idxField = defn.GetFieldIndex( fieldName )
        if not updateField:
            if idxField > -1:
                msg = f"Point Layer '{pathfile}' has field '{fieldName}'"
                return { 'isOk': False, 'message': msg }
            return { 'isOk': True, 'datasource': ds, 'layer': layer }
        if idxField == -1:
            msg = f"Point Layer '{pathfile}' missing field '{fieldName}'"
            return { 'isOk': False, 'message': msg }
        fieldDefn = defn.GetFieldDefn( idxField )
        if not fieldDefn.GetType() in LayerValuePixels.TYPEBAND2FIELD.values():
            name = fieldDefn.GetTypeName()
            msg = f"Point Layer '{pathfile}' type field '{fieldName}' is invalid '{name}'"
            return { 'isOk': False, 'message': msg }

        return { 'isOk': True, 'datasource': ds, 'layer': layer }

    @staticmethod
    def getDataSet(pathfile, nBand):
        if not os.path.isfile( pathfile ):
            msg = f"Missing file '{pathfile}'"
            return { 'isOk': False, 'message': msg }
        ds = gdal.Open( pathfile )
        if ds is None:
            msg = f"Error read image '{pathfile}'"
            return { 'isOk': False, 'message': msg }
        if ds.GetSpatialRef() is None:
            ds = None
            msg = f"Image '{pathfile}' missing Spatial Reference"
            return { 'isOk': False, 'message': msg }
        if ds.RasterCount < nBand:
            ds = None
            msg = "Image '{pathfile}' missing Band '{nBand}'"
            return { 'isOk': False, 'message': msg }
        band = ds.GetRasterBand( nBand )
        if not band.DataType in LayerValuePixels.TYPEBAND2FIELD:
            band = None
            ds = None
            name = gdal.GetDataTypeName( band.DataType )
            msg = f"Image '{pathfile}' type Band '{nBand}' is invalid '{name}'"
            return { 'isOk': False, 'message': msg }
        band = None

        return { 'isOk': True, 'dataset': ds }

    def __init__(self, dsImage, nBand, layerPoint, fieldName, updateField):
        self.vp = ValuePixel( dsImage )
        self.vp.setBand( nBand )
        self.layer, self.fieldName = layerPoint, fieldName
        self.ct = None
        self.idxField = -1 if updateField else None

    def init(self):
        # Coordinate Transform
        srLayer = self.layer.GetSpatialRef()
        srImage = self.vp.ds.GetSpatialRef()
        if not srLayer == srImage:
            self.ct = osr.CoordinateTransformation( srLayer, srImage )
        # Field
        defn = self.layer.GetLayerDefn()
        if self.idxField == -1: # Update field
            idxField = defn.GetFieldIndex( self.fieldName )
            self.layer.DeleteField( idxField )
        # Create Field
        typeField = self.TYPEBAND2FIELD[ self.vp.band.DataType ]
        fieldDefn = ogr.FieldDefn( self.fieldName, typeField )
        self.layer.CreateField( fieldDefn )
        self.idxField = defn.GetFieldIndex( self.fieldName )
        self.layer.SyncToDisk()
        return { 'isOk': True }

    def addValues(self, printStatus):
        def getGeomCoordTrans(geom):
            g = geom.Clone()
            g.Transform( self.ct )
            return g

        insideImage = lambda x, y: (
            self.vp.boundBoxImage['minX'] <= x <= self.vp.boundBoxImage['maxX'] and \
            self.vp.boundBoxImage['minY'] <= y <= self.vp.boundBoxImage['maxY']
        )
        f_trans = getGeomCoordTrans if not self.ct is None \
            else lambda geom: geom
        c_points, total_points = 0, self.layer.GetFeatureCount()
        for feat in self.layer:
            c_points += 1
            msg = f"Processing point {c_points} of {total_points}"
            printStatus( msg )
            # Geom
            geom = feat.GetGeometryRef()
            geomT = f_trans( geom )
            # Add value pixel
            x, y = geomT.GetX(), geomT.GetY()
            if not insideImage( x, y ):
                continue
            value = self.vp(  x, y )
            feat.SetField( self.idxField, value )
            self.layer.SetFeature( feat )
            feat = None
        self.layer.SyncToDisk()
        printStatus( 'Finished!', True)


def run(image, nBand, shapefile, fieldName, updateField):
    def printStatus(status, newLine=False):
        if newLine:
            ch = "\n"
        else:
            ch = ""
        sys.stdout.write( "\r{}".format( status.ljust(100) + ch ) )
        sys.stdout.flush()

    r = LayerValuePixels.getLayerPoint( shapefile, fieldName, updateField )
    if not r['isOk']:
        printStatus( r['message'], True )
        return 1
    _dsPoint, layerPoint = r['datasource'], r['layer']
    r = LayerValuePixels.getDataSet( image, nBand )
    if not r['isOk']:
        printStatus( r['message'], True )
        _dsPoint = None
        return 1
    dsImage = r['dataset']

    lvp = LayerValuePixels( dsImage, nBand, layerPoint, fieldName, updateField )
    r = lvp.init()
    if not r['isOk']:
        printStatus( r['message'], True )
        _dsPoint = None
        dsImage = None
        return 1

    lvp.addValues( printStatus )
    _dsPoint = None
    dsImage = None

    return 0

def main():
    parser = argparse.ArgumentParser(description="Add values image's pixel of point inside shapefile" )
    parser.add_argument('image', type=str, help='Pathfile image')
    parser.add_argument('nband', type=int, help='Number of band')
    parser.add_argument('shapefile', type=str, help='Pathfile shapefile of Points')
    parser.add_argument('field_name', type=str, help="'Field's name of Shapefile for values of pixels")
    parser.add_argument( '-u', '--update', action="store_true", help='Update field' )

    args = parser.parse_args()
    return run( args.image, args.nband, args.shapefile, args.field_name, args.update )


if __name__ == "__main__":
    sys.exit( main() )

