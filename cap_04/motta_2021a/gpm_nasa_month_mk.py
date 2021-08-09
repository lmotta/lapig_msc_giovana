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


import sys, os, glob, argparse
import pymannkendall as mk
import numpy as np

from osgeo import gdal, gdal_array
from gdalconst import GA_ReadOnly, GA_Update

def createOutDSMem(filename, c_band, type, descriptions):
    ds_origin = gdal.Open( filename, GA_ReadOnly )
    xsize, ysize = ds_origin.RasterXSize, ds_origin.RasterYSize
    transform = ds_origin.GetGeoTransform()
    #
    drv = gdal.GetDriverByName('MEM')
    ds = drv.Create('', xsize, ysize, c_band, type )
    ds.SetGeoTransform( transform )
    ds.SetProjection( ds_origin.GetProjection() )
    ds.SetSpatialRef( ds_origin.GetSpatialRef() )
    ds_origin = None
    for idx in range(c_band):
        b = ds.GetRasterBand( idx+1 )
        b.SetDescription( descriptions[idx] )
    return ds

def readArray(filename, n_band):
    ds = gdal.Open( filename, GA_ReadOnly )
    band = ds.GetRasterBand( n_band )
    dtype = gdal_array.GDALTypeCodeToNumericTypeCode(gdal.GDT_Float32)
    arry = band.ReadAsArray().astype( dtype )
    #
    nodata = band.GetNoDataValue()
    ds = None
    return arry, nodata

def createTifByDataset(filename, ds):
    drv = gdal.GetDriverByName('GTiff')
    ds_out = drv.CreateCopy( filename, ds )
    ds_out = None

def populateDS(ds, arry):
    total_images, _y, _x = arry.shape
    if not ds.RasterCount == total_images:
        return
    for idx in range(ds.RasterCount):
        band = ds.GetRasterBand( idx+1)
        band.WriteArray( arry[idx] )
    ds.FlushCache()

def getValuesMK(arry, p_sig):
    z_, lines, cols = arry.shape
    arryMk = np.ndarray( ( 3, lines, cols ) )
    for l in range(lines):
        for c in range(cols):
            v = arry[:, l, c ]
            if  np.isnan( np.sum(v) ):
                arryMk[0, l, c] = np.nan
                arryMk[1, l, c] = np.nan
                arryMk[2, l, c] = np.nan
                continue
            r = mk.original_test( v, p_sig )
            arryMk[0, l, c] = r.s if r.p <= p_sig else np.nan
            arryMk[1, l, c] = r.p
            arryMk[2, l, c] = r.slope if r.p <= p_sig else np.nan
    return arryMk

def processMK(images_dir, prefix_img, p_sig, month):
    suffix = 'total.accum'  # cerrado_2000_06_total.accum
    name = f"{prefix_img}_*_{month}_{suffix}.tif"
    filter = os.path.join( images_dir, name )
    filenames = sorted( glob.glob( filter ) )
    total_images = len( filenames )
    print(f". Processing month: {month} ( {total_images} images)...")
    # Create DataSet
    ds = createOutDSMem(filenames[0], 3, gdal.GDT_Float32, [ 's_mk', f"p_{p_sig}", 'slope'] )
    # Create Array with N images
    arry = np.ndarray( ( total_images, ds.RasterYSize, ds.RasterXSize ) )
    for i, f in enumerate( filenames ):
        band, nodata = readArray( f, 1 )
        band[ band == nodata ] = np.nan
        #arry[i:] = band # Copy [i:]
        arry[i] = band
    #
    arryMk = getValuesMK( arry, p_sig )
    del arry
    populateDS(ds, arryMk)
    #
    filename = f"{prefix_img}_{month}_{suffix}_mk.tif"
    # filename = os.path.join( images_dir, filename )
    createTifByDataset( filename, ds )
    ds = None


gdal.AllRegister()
gdal.UseExceptions()

def run(images_dir, prefix_img, p_sig):
    months = [ f"{m:02d}" for m in range(1,13) ]
    for m in months:
        processMK(images_dir, prefix_img, p_sig, m )

def main():
    parser = argparse.ArgumentParser(description=f"Create images with Mann kendall statistics from  GPM images." )
    parser.add_argument( 'images_dir', action='store', help='Directory with images', type=str)
    parser.add_argument( 'prefix_img', action='store', help='Preffix of images(ex.:cerrado_2000_06_total.accum)', type=str)
    parser.add_argument( '--p_sig', action='store', default=0.05, help='Significance level(default: 0.05)', type=float)

    args = parser.parse_args()
    return run( args.images_dir, args.prefix_img, args.p_sig )

if __name__ == "__main__":
    sys.exit( main() )
