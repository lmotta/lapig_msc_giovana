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

import sys, os, glob, struct, argparse
import numpy as np

from osgeo import gdal, gdal_array
from gdalconst import GA_ReadOnly

gdal.UseExceptions()
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.SetCacheMax (1000000000)


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def createResultDS(ds_origin, filename):
    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create(filename, ds_origin.RasterXSize, ds_origin.RasterYSize, 1, gdal.GDT_Byte )
    ds.SetGeoTransform( ds_origin.GetGeoTransform() )
    ds.SetSpatialRef( ds_origin.GetSpatialRef() )
    band = ds.GetRasterBand(1)
    band.SetDescription('Slope(1:CER,2:NEG,3:NONE,4:POS,5:ALT)')
    band.SetNoDataValue( 0 )
    return ds

def populateResult(filename, slopes_p005):
    def process(band, yoff, cols):
        def getResult():
            """
            0: NoData
            1: CER
            2: NEG
            3: NONE
            4: POS
            5: ALT
            """
            size = arryColSlope.size
            totalNanP005 = np.isnan(arryColP005).sum().item()
            totalNanSlope = np.isnan(arryColSlope).sum().item()
            if totalNanSlope == size:
                return 0 if totalNanP005 == size else 1
            arry = arryColSlope[~np.isnan( arryColSlope )] # Remove NaN
            totalNeg = ( arry < 0.0).sum().item()
            totalNone = ( arry == 0.0).sum().item()
            totalPos = ( arry > 0.0).sum().item()
            if (totalNeg + totalNanSlope ) == size:
                return 2
            if (totalNone + totalNanSlope ) == size:
                return 3
            if (totalPos + totalNanSlope ) == size:
                return 4
            return 5
            
        rows = len( slopes_p005 )
        size = ( rows, cols )
        arrySlope = np.ndarray( size, dtype=dtype_in )
        arryP005 = np.ndarray( size, dtype=dtype_in )
        for idx in range( rows ):
            arrySlope[ idx ] = slopes_p005[idx]['slope'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
            arryP005[ idx ]  = slopes_p005[idx]['p005'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
        arryResult = np.ndarray( ( 1, cols ), dtype=dtype_out )
        for idy in range( cols ):
            arryColSlope = arrySlope[:, idy ] # Months
            arryColP005 = arryP005[:, idy ] # Months
            arryResult[ 0, idy ] = getResult()
        band.WriteArray( arryResult, 0, yoff ) # xoff, yoff
        band.FlushCache()
        del arrySlope, arryP005, arryResult, arryColSlope, arryColP005

    dsResult = createResultDS( slopes_p005[0]['ds'], filename )
    band = dsResult.GetRasterBand(1)
    dtype_in = gdal_array.GDALTypeCodeToNumericTypeCode( gdal.GDT_Float32 )
    dtype_out = gdal_array.GDALTypeCodeToNumericTypeCode( gdal.GDT_Byte )
    xsize = dsResult.RasterXSize
    ysize = dsResult.RasterYSize
    for y in range( 0, ysize):
        printProgressBar(y + 1, ysize, prefix=filename, suffix='Complete', length = 50)
        process( band, y, xsize )
    dsResult = None

def run(dir_tendences):
    def getBands(name):
        filter = os.path.join( dir_tendences, f"{name}.tif" )
        filenames = sorted( glob.glob( filter ) )
        data = []
        for fn in filenames:
            ds = gdal.Open( fn, GA_ReadOnly )
            d = {
                'ds': ds,
                'p005': ds.GetRasterBand(2),
                'slope': ds.GetRasterBand(3)                
            }
            data.append( d )
        return data

    name = 'cerrado_*_total.accum_mk'
    slopes_p005 = getBands( name )
    filename = f"{name.replace('_*_','_')}_reduce.tif"
    populateResult( filename, slopes_p005 )
    for t in slopes_p005:
        t['ds'] = None

def main():
    parser = argparse.ArgumentParser(description=f"Reduce tendences from cerrado_MONTH_total.accum_mk - SLOPE." )
    parser.add_argument( 'dir_tendences', action='store', help='Directory of tendences(Ex.: antropico_mk)', type=str)

    args = parser.parse_args()
    return run( args.dir_tendences )

if __name__ == "__main__":
    sys.exit( main() )
