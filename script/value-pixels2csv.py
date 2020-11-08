#!/usr/bin/python3
# # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Value pixels to Csv
Description          : Read points from shapefile and 
                       get values pixels from images for save in CSV
Date                 : October, 2019
copyright            : (C) 2019 by Luiz Motta
email                : motta.luiz@gmail.com

 ***************************************************************************/

Dependences:
- mod_py.valuepixel

Update:
- 2020-09-02:
Change value pixel calc

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys, csv
import struct
import argparse

try:
    from osgeo import ogr, osr, gdal
except ImportError:
    import ogr, osr
gdal.UseExceptions()

from mod_py.valuepixel import ValuePixel


class GetValuePixels():
    def __init__(self):
        self.dsCatalog, self.layerCatalog = None, None
        self.dsPoints,  self.layerPoints = None, None
        self.nameFidPoints = None
    
    def __del__(self):
        self.dsPoints = None
        self.dsCatalog = None

    def init(self, dirImages, shapefile, nameFid, printStatus):
        def setLayerPoints():
            if not os.path.isfile( shapefile ):
                msg = f"Missing file '{shapefile}'"
                return { 'isOk': False, 'message': msg }
            driver = ogr.GetDriverByName('ESRI Shapefile')
            ds = driver.Open( shapefile, 0 )
            if ds is None:
                msg = f"Error read Shapefile '{shapefile}'"
                return { 'isOk': False, 'message': msg }
            layer = ds.GetLayer()
            if layer is None:
                msg = f"Error read Shapefile '{shapefile}'"
                return { 'isOk': False, 'message': msg }
            if not layer.GetGeomType() == ogr.wkbPoint:
                msg = f"Geometry type of Shapefile '{shapefile}' need be a POINT"
                return { 'isOk': False, 'message': msg }
            defn = layer.GetLayerDefn()
            idxField = defn.GetFieldIndex( nameFid )
            if idxField == -1:
                msg = f"Missing field '{nameFid}' in Shapefile '{shapefile}'"
                return { 'isOk': False, 'message': msg }
            self.dsPoints = ds, self.layerPoints, self.nameFidPoints = ds, layer, nameFid
            return { 'isOk': True }

        def setLayerCatalog(srCatalog):
            def createLayer():
                drv = ogr.GetDriverByName('MEMORY')
                self.dsCatalog =  drv.CreateDataSource('memData')
                self.layerCatalog = self.dsCatalog.CreateLayer('catalog', srs=srCatalog, geom_type=ogr.wkbPolygon )
                fields = [
                    { 'name': 'path', 'type': ogr.OFTString, 'width': 200 }
                ]
                for item in fields:
                    f = ogr.FieldDefn( item['name'], item['type'] )
                    if 'width' in item:
                        f.SetWidth( item[ 'width' ] )
                    self.layerCatalog.CreateField( f )

            def createFeature(dsImage, srImage, defn):
                def getGeomExtent():
                    # (x, y) origin of the top left pixel
                    TL_x, x_res, _x_rotation, TL_y, _y_rotation, y_res = dsImage.GetGeoTransform()
                    minX, maxY = TL_x, TL_y
                    maxX = minX + x_res * dsImage.RasterXSize
                    minY = maxY + y_res * dsImage.RasterYSize
                    ring = ogr.Geometry( ogr.wkbLinearRing )
                    ring.AddPoint( minX, minY )
                    ring.AddPoint( minX, maxY )
                    ring.AddPoint( maxX, maxY )
                    ring.AddPoint( maxX, minY )
                    ring.AddPoint( minX, minY )
                    geom = ogr.Geometry( ogr.wkbPolygon )
                    geom.AddGeometry( ring )
                    return geom

                ct = osr.CoordinateTransformation( srImage, srCatalog )
                geom = getGeomExtent()
                geom.Transform( ct )
                item = {
                    'path': dsImage.GetDescription()
                }
                feat = ogr.Feature( defn )
                feat.SetGeometry( geom )
                for k in item:
                    feat.SetField( k, item[ k ] )
                self.layerCatalog.CreateFeature( feat )

            if not os.path.isdir( dirImages):
                msg = "Missing directory '{dirImages}'"
                return { 'isOk': False, 'message': msg }
            
            createLayer()
            defn = self.layerCatalog.GetLayerDefn()
            srImage = osr.SpatialReference()
            images = os.listdir( dirImages )
            c_img, total_img = 0, len( images )
            for img in images:
                try:
                    img = f"{dirImages}{os.path.sep}{img}"
                    ds = gdal.Open( img ) # If error go to except
                    srImage = ds.GetSpatialRef()
                    createFeature( ds, srImage, defn )
                    c_img += 1
                    msg = f"Populate catalog images {c_img} of {total_img}..."
                    printStatus( msg )
                    ds = None
                except:
                    pass
            self.layerCatalog.SyncToDisk()
            if self.layerCatalog.GetFeatureCount() == 0:
                msg = f"Directory '{dirImages}' is empty"
                return { 'isOk': False, 'message': msg }
            return { 'isOk': True }

        r = setLayerPoints()
        if not r['isOk']:
            return r
        return setLayerCatalog( self.layerPoints.GetSpatialRef() )

    def getValues(self, printStatus):
        def getValuePixel(geomPoint, srPoint, pathImage, nBand):
            def getXYGeom(dsImage):
                srImage = dsImage.GetSpatialRef()
                if srImage == srPoint:
                    ct = osr.CoordinateTransformation( srPoint, srImage )
                    geomT = geomPoint.Clone()
                    geomT.Transform( ct )
                else:
                    geomT = geomPoint
                return ( geomT.GetX(), geomT.GetY() )

            ds = gdal.Open( pathImage )
            args = getXYGeom( ds )
            vp = ValuePixel( ds )
            vp.setBand( nBand )

            return vp( *args )

        srPoint = self.layerPoints.GetSpatialRef()
        values = []
        c_points, total_points = 0, self.layerPoints.GetFeatureCount()
        c_points_in_image = 0
        for featPoint in self.layerPoints:
            c_points += 1
            msg = f"Processing point {c_points} of {total_points}"
            printStatus( msg )
            valueFid = featPoint[ self.nameFidPoints ]
            geom = featPoint.GetGeometryRef()
            self.layerCatalog.SetSpatialFilter( geom )
            for featCatalog in self.layerCatalog:
                v_pixel = getValuePixel( geom, srPoint, featCatalog['path'], 1 )
                value = [ valueFid, featCatalog['path'], v_pixel ]
                values.append( value )
                c_points_in_image += 1
            self.layerCatalog.SetSpatialFilter( None )
        r = { 'header': [ self.nameFidPoints, 'image', 'pixel_value'], 'values': values, 'c_points_in_image': c_points_in_image }
        return r


def run(dirImages, shapefile, nameFid ):
    def printStatus(status, newLine=False):
        if newLine:
            ch = "\n"
        else:
            ch = ""
        sys.stdout.write( "\r{}".format( status.ljust(100) + ch ) )
        sys.stdout.flush()

    def saveCsv(path_file, data):
        with open( path_file, mode='w') as f:
            f_writer = csv.writer( f, delimiter=';' )
            f_writer.writerow( data['header'] )
            for item in data['values']:
                f_writer.writerow( item )

    c = GetValuePixels()
    r = c.init( dirImages, shapefile, nameFid, printStatus )
    if not r['isOk']:
        printStatus( r['message'], True)
        return 0

    r = c.getValues( printStatus )

    total_points = c.layerPoints.GetFeatureCount()
    total_images = c.layerCatalog.GetFeatureCount()
    total_point_in_image = r['c_points_in_image']
    l_msg = [
        "Shapefile(points): {}".format( total_points ),
        "Directory(images): {}".format( total_images ),
        "- Points in images: {}".format( total_point_in_image )
    ]
    [ printStatus( msg, True ) for msg in l_msg ]

    path_file = os.path.splitext( shapefile )[0]
    if total_point_in_image > 0:
        p_f = "{}{}".format( path_file, '_images.csv')
        saveCsv( p_f, r )
        msg = "Saved {}".format( p_f )
        printStatus( msg, True )
    return 0

def main():
    parser = argparse.ArgumentParser(description='Get Value pixels from points, creating CSV with values' )
    parser.add_argument('dir_images', type=str, help='Directory with images')
    parser.add_argument('shapefile', type=str, help='Shapefile of points')
    parser.add_argument('name_fid', type=str, help="'Field's name of Shapefile with unique values(for Join)")

    args = parser.parse_args()
    return run( args.dir_images, args.shapefile, args.name_fid )


if __name__ == "__main__":
    sys.exit( main() )
