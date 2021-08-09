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

def printStatistic(statistic):
    def message(tend):
        values = [
            f"Min: {statistic[ tend ]['min']}",
            f"Mean: {statistic[ tend ]['mean']}",
            f"Max: {statistic[ tend ]['max']}",
            f"Count: {statistic[ tend ]['count']}"
        ]
        return '\n'.join( values )

    for tend in ('neg', 'none' ,'pos'):
        if not statistic[ tend ]['count']:
            msg = f"\n{tend.upper()}: NONE"
            print(msg)
            continue
        statistic[ tend ]['mean'] = statistic[ tend ]['sum'] / statistic[ tend ]['count']
        msg = f"\n{tend.upper()}:\n{message( tend )}"
        print(msg)

def calcValues(total_statistic, statistic):
    for tend in ('neg', 'none' ,'pos'):
        if not total_statistic[ tend ]['count']:
            total_statistic[ tend ]['count'] =  statistic[ tend ]['count']
            total_statistic[ tend ]['sum']   =  statistic[ tend ]['sum']
            total_statistic[ tend ]['max']   = statistic[ tend ]['max']
            total_statistic[ tend ]['min']   = statistic[ tend ]['min']
            continue

        if not statistic[ tend ]['count']:
            continue

        total_statistic[ tend ]['count'] +=  statistic[ tend ]['count']
        total_statistic[ tend ]['sum']   +=  statistic[ tend ]['sum']
        if total_statistic[ tend ]['max'] < statistic[ tend ]['max']:
            total_statistic[ tend ]['max'] = statistic[ tend ]['max']
        if total_statistic[ tend ]['min'] > statistic[ tend ]['min']:
            total_statistic[ tend ]['min'] = statistic[ tend ]['min']

def getStatistic(slope, arryStatus, values_status):
    def getValues(arry):
        count = arry.size
        if not count:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'sum': None
            }
        return {
            'count': arry.size,
            'min': arry.min().item(),
            'max': arry.max().item(),
            'sum': arry.sum().item()
        }

    arry = slope['band'].ReadAsArray()
    valid = ~np.isnan( arry )
    r = {}
    for tend in values_status:
        r[ tend ] = getValues( arry[ valid & ( arryStatus ==  values_status[ tend ] ) ] )
    return r

def getArryStatus(filename, n_band):
    ds = gdal.Open( filename, GA_ReadOnly )
    arry = ds.GetRasterBand( n_band ).ReadAsArray()
    ds = None
    return arry

def getBandsSlope(dir_tendences, name):
    filter = os.path.join( dir_tendences, f"{name}.tif" )
    filenames = sorted( glob.glob( filter ) )
    data = []
    for fn in filenames:
        ds = gdal.Open( fn, GA_ReadOnly )
        d = {
            'ds': ds,
            'band': ds.GetRasterBand(3)                
        }
        data.append( d )
    return data

def run(dir_tendences, filename_reduce):
    name = 'cerrado_??_total.accum_mk' # cerrado_01_total.accum_mk
    slopes = getBandsSlope( dir_tendences, name )
    totalfiles = len( slopes )

    arryStatus = getArryStatus( filename_reduce, 5 )

    title = f"Calculating total statistic(1 of {totalfiles})"
    printProgressBar(1, totalfiles, title, suffix='Complete', length = 50)
    value_status = { 'neg': 2, 'none': 3, 'pos': 4 }
    total_statistic = getStatistic( slopes[0], arryStatus, value_status ) # { neg: { min, sum, count, max }, none:{...}, pos: {...}
    slopes[0]['ds'] = None
    for idx, slope  in enumerate( slopes[1:]):
        title = f"Calculating total statistic({idx+2} of {totalfiles})"
        printProgressBar(idx+2, totalfiles, title, suffix='Complete', length = 50)
        v = getStatistic( slope, arryStatus, value_status )
        slope['ds'] = None
        calcValues( total_statistic, v )
    printStatistic( total_statistic )

def main():
    parser = argparse.ArgumentParser(description=f"Total values of min,mean,max from reduce tendences(cerrado_MONTH_total.accum_mk - SLOPE)." )
    parser.add_argument( 'dir_tendences', action='store', help='Directory of tendences(Example of files: cerrado_01_total.accum_mk.tif)', type=str)
    parser.add_argument( 'filename_reduce', action='store', help='Filename reduce(Ex.:cerrado_total.accum_mk_reduce_min-mean-max.tif)', type=str)

    args = parser.parse_args()
    return run( args.dir_tendences, args.filename_reduce )

if __name__ == "__main__":
    sys.exit( main() )
