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

import sys, argparse


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

def getStatistic(bands, yoff, cols):
    # Status
    arryStatus = bands['status'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
    arryNeg = ( arryStatus == 2 )
    arryPos = ( arryStatus == 4 )
    arryMin = bands['min'].ReadAsArray( 0, yoff, win_ysize=1 )
    arryMean = bands['mean'].ReadAsArray( 0, yoff, win_ysize=1 )
    arryMax = bands['max'].ReadAsArray( 0, yoff, win_ysize=1 )
    # Min
    neg_count = arryNeg.sum()
    if neg_count == 0:
        neg_min = None
        neg_max = None
        neg_mean_sum = 0
    else:
        neg_min = arryMin[ arryNeg ].min().item()
        neg_max = arryMax[ arryNeg ].max().item()
        neg_mean_sum = arryMean[ arryNeg ].sum().item()
    # Max
    pos_count = arryPos.sum()
    if pos_count == 0:
        pos_min = None
        pos_max = None
        pos_mean_sum = 0
    else:
        pos_min = arryMin[ arryPos ].min().item()
        pos_max = arryMax[ arryPos ].max().item()
        pos_mean_sum = arryMean[ arryPos ].sum().item()

    result = {
        'neg_count': neg_count, 'neg_min': neg_min, 'neg_max': neg_max, 'neg_mean_sum': neg_mean_sum,
        'pos_count': pos_count, 'pos_min': pos_min, 'pos_max': pos_max, 'pos_mean_sum': pos_mean_sum
    }
    del arryStatus, arryNeg, arryPos, arryMin, arryMean, arryMax
    return result

def run(filename):
    """
    Bands: 1.min, 2.mean, 3.max, 4.count, 5.Status(1:CER,2:NEG,3:NONE,4:POS,5:ALT)
    """
    def setValueStatistic(key):
        cmpValue = lambda s, r: s > r # Minimum
        if not key.find('max') == -1: # Maximum
            cmpValue = lambda s, r: s < r
        if statistic[ key ]:
            if r[ key ] and cmpValue( statistic[ key ], r[ key ] ):
                statistic[ key ] = r[ key ]
            return
        if r[ key ]:
            statistic[ key ] = r[ key ]

    ds = gdal.Open( filename, GA_ReadOnly )
    bands = {
        'min': ds.GetRasterBand(1),
        'mean': ds.GetRasterBand(2),
        'max': ds.GetRasterBand(3),
        'status': ds.GetRasterBand(5),
    }
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    statistic = getStatistic( bands, 0, xsize ) # { neg_count, neg_min, neg_max, neg_mean_sum, pos_...}
    for y in range( 1, ysize):
        printProgressBar(y + 1, ysize, prefix=filename, suffix='Complete', length = 50)
        r = getStatistic( bands, y, xsize )
        statistic['neg_count'] += r['neg_count']
        statistic['neg_mean_sum'] += r['neg_mean_sum']
        setValueStatistic('neg_min')
        setValueStatistic('neg_max')

        statistic['pos_count'] += r['pos_count']
        statistic['pos_mean_sum'] += r['pos_mean_sum']
        setValueStatistic('pos_min')
        setValueStatistic('pos_max')
    ds = None
    statistic['neg_mean'] = statistic['neg_mean_sum'] / statistic['neg_count']
    statistic['pos_mean'] = statistic['pos_mean_sum'] / statistic['pos_count']

    msg = f"Tendeces NEG\nMin: {statistic['neg_min']}\nMean: {statistic['neg_mean']}\nMax: {statistic['neg_max']}"
    print( msg )
    msg = f"\nTendeces POS\nMin: {statistic['pos_min']}\nMean: {statistic['pos_mean']}\nMax: {statistic['pos_max']}"
    print( msg )


def main():
    parser = argparse.ArgumentParser(description=f"Get values MIN, MEAN, MAX of tendences(POS and NEG)." )
    parser.add_argument( 'filename', action='store', help='File name of MIN MEAN MAX(Ex.: cerrado_total.accum_mk_reduce_min-mean-max.tif)', type=str)

    args = parser.parse_args()
    return run( args.filename )

if __name__ == "__main__":
    sys.exit( main() )
