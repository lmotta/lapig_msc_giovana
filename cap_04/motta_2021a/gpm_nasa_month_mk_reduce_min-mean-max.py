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

def createResultDS(ds_origin, filename, nodata):
    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create(filename, ds_origin.RasterXSize, ds_origin.RasterYSize, 5, gdal.GDT_Float32 )
    ds.SetGeoTransform( ds_origin.GetGeoTransform() )
    ds.SetSpatialRef( ds_origin.GetSpatialRef() )
    descs = (
        'min', 'mean', 'max', 'count',
        'Status(1:CER,2:NEG,3:NONE,4:POS,5:ALT)'
    )
    for idx, value in enumerate( descs ):
        band = ds.GetRasterBand( idx+1)
        band.SetDescription( value )
        band.SetNoDataValue( nodata )
    return ds

def populateResult(filename, slopes_p005):
    def process(bands, yoff, cols):
        def getResults():
            """
            Return: [
                min, mean, max, count,
                Status(0:NODATA,1:CER,2:NEG,3:NONE,4:POS,5:ALT)
            ]
            """
            nodataBand = bands[0].GetNoDataValue()
            results = [ nodataBand ] * 5
            size = arryColSlope.size
            totalNanP005 = np.isnan(arryColP005).sum().item()
            totalNanSlope = np.isnan(arryColSlope).sum().item()
            if totalNanSlope == size:
                if totalNanP005 == size: # Nodata -> Out CER
                    return results
                results[-1] = 1.0 # No significant
                return results

            arry = arryColSlope[~np.isnan( arryColSlope )] # Remove NaN
            arryNeg = ( arry < 0.0 )
            arryNone = ( arry == 0.0 )
            arryPos = ( arry > 0.0 )
            totalNeg = arryNeg.sum().item()
            totalNone = arryNone.sum().item()
            totalPos = arryPos.sum().item()
            arryMinMedMax = None
            if ( totalNeg + totalNanSlope ) == size:
                results[-2] = totalNeg
                results[-1] = 2.0
                arryMinMedMax = arry[ arryNeg ]
            elif ( totalNone + totalNanSlope ) == size:
                results[-2] = totalNone
                results[-1] = 3.0
            elif ( totalPos + totalNanSlope ) == size:
                results[-2] = totalPos
                results[-1] = 4.0
                arryMinMedMax = arry[ arryPos ]
            else:
                results[-2] = totalNeg + totalNone + totalPos
                results[-1] = 5.0
            if not arryMinMedMax is None:
                results[:3] = [ arryMinMedMax.min(), arryMinMedMax.mean(), arryMinMedMax.max() ]
            return results
            
        rows = len( slopes_p005 )
        size = ( rows, cols )
        arrySlope = np.ndarray( size, dtype=dtype )
        arryP005 = np.ndarray( size, dtype=dtype )
        for idx in range( rows ):
            arrySlope[ idx ] = slopes_p005[idx]['slope'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
            arryP005[ idx ]  = slopes_p005[idx]['p005'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
        arryResults = np.ndarray( ( len( bands ), 1, cols ), dtype=dtype )
        for idy in range( cols ):
            arryColSlope = arrySlope[:, idy ] # Months
            arryColP005 = arryP005[:, idy ] # Months
            for idx, r in enumerate( getResults() ):
                arryResults[ idx, 0, idy ] = r
        for idx, b in enumerate( bands ):
            b.WriteArray( arryResults[ idx ], 0, yoff ) # xoff, yoff
            b.FlushCache()
        del arrySlope, arryP005, arryResults, arryColSlope, arryColP005

    dsResult = createResultDS( slopes_p005[0]['ds'], filename, 0 )
    bands = [ dsResult.GetRasterBand( idx+1 ) for idx in range( dsResult.RasterCount ) ]
    dtype = gdal_array.GDALTypeCodeToNumericTypeCode( gdal.GDT_Float32 )
    xsize = dsResult.RasterXSize
    ysize = dsResult.RasterYSize
    for y in range( 0, ysize):
        printProgressBar(y + 1, ysize, prefix=filename, suffix='Complete', length = 50)
        process( bands, y, xsize )
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
    filename = f"{name.replace('_*_','_')}_reduce_min-mean-max.tif"
    populateResult( filename, slopes_p005 )
    for t in slopes_p005:
        t['ds'] = None

def main():
    parser = argparse.ArgumentParser(description=f"Reduce tendences(min,med,max) from cerrado_MONTH_total.accum_mk - SLOPE." )
    parser.add_argument( 'dir_tendences', action='store', help='Directory of tendences(Example of files: cerrado_01_total.accum_mk.tif)', type=str)

    args = parser.parse_args()
    return run( args.dir_tendences )

if __name__ == "__main__":
    sys.exit( main() )
