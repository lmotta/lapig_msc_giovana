#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Scripts for Msc of Giovana in LAPIG(University of Goias)
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
__date__ = '2021-08-01'
__copyright__ = '(C) 2021, Luiz Motta'
__revision__ = '$Format:%H$'

import sys, os, argparse
import numpy as np

from osgeo import gdal, ogr, gdal_array
from gdalconst import GA_ReadOnly, GA_Update

def getArgsClip(ds_vector, ds_image):
    lyr = ds_vector.GetLayer(0)
    minx, maxx, miny, maxy = lyr.GetExtent()
    #
    gt = ds_image.GetGeoTransform()
    #
    left = minx - (minx - gt[0]) % gt[1]
    right = maxx + (gt[1] - ((maxx - gt[0]) % gt[1]))
    bottom = miny + (gt[5] - ((miny - gt[3]) % gt[5]))
    top = maxy - (maxy - gt[3]) % gt[5]
    #    
    return {
        'outputBounds': ( left, bottom, right, top ),
        'xRes': abs( gt[1] ),
        'yRes': abs( gt[5] )
    }

def createWarp(image, args, shapefile, format):
    args['cutlineDSName'] = shapefile
    args['cutlineLayer'] = os.path.basename( shapefile ).split('.')[0]
    args['format'] = format
    args['cutlineBlend'] = 0.5
    args['dstNodata'] = 29999
    args['multithread'] = True
    args['copyMetadata'] = False
    args = gdal.WarpOptions( **args )
    return gdal.Warp( '', image, options=args)

def writeTiff(ds, filename):
    drv = gdal.GetDriverByName('GTiff')
    ds_out = drv.CreateCopy( filename, ds)
    ds_out = None

gdal.AllRegister()
gdal.UseExceptions()

def run(image, shp, prefix):
    ds_image = gdal.Open( image, GA_ReadOnly )
    ds_vector = ogr.Open( shp )

    v_date = os.path.basename(image).split('-')[2].split('.')[-1]
    aaaa = v_date[:4]
    mm = v_date[4:6]
    image_clip = f"{prefix}_{aaaa}_{mm}_total.accum.tif"
    if os.path.isfile( image_clip ):
        os.remove( image_clip )
    #
    args = getArgsClip( ds_vector, ds_image )
    ds_image = None
    ds_vector = None
    print(f"{image_clip}")
    ds_mem = createWarp( image, args, shp, 'MEM')
    writeTiff( ds_mem, image_clip )
    ds_mem = None

def main():
    parser = argparse.ArgumentParser(description='Clip raster by shapefile.' )
    parser.add_argument( 'image', action='store', help='Filepath of image', type=str)
    parser.add_argument( 'shp', action='store', help='Filepath of shapefile', type=str)
    parser.add_argument( 'prefix', action='store', help='Prefix of Clip image', type=str)

    args = parser.parse_args()
    return run( args.image, args.shp, args.prefix )

if __name__ == "__main__":
    sys.exit( main() )
