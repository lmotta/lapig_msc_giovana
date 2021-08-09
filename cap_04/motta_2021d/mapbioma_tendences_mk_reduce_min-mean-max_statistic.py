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

def getStatistic(class_map, bands, yoff, cols):
    """
    {
        class_map_1: {
            neg: { count, min, max, mean_sum },
            pos: { count, min, max, mean_sum }
        },
        class_map_2...
    }
    """
    def setClassMap(value):
        def getMinMeanSumMax(arryTendence):
            count = arryTendence.sum()
            result = { 'count': count, 'min': None, 'max': None, 'mean_sum': 0 }
            if count > 0:
                result = {
                    'count': count,
                    'min': arryMin[ arryTendence ].min().item(),
                    'max': arryMax[ arryTendence ].max().item(),
                    'mean_sum': arryMean[ arryTendence ].sum().item()
                }
            return result
                
        
        arry_neg = ( ( arryMap == value ) & ( arryStatus == 2 ) )
        arry_pos = ( ( arryMap == value ) & ( arryStatus == 4 ) )
        tend_neg = getMinMeanSumMax( arry_neg )
        tend_pos = getMinMeanSumMax( arry_pos )
        result =  {
            'neg': tend_neg,
            'pos': tend_pos
        }
        del arry_neg, arry_pos
        return result
    #
    arryMap = bands['map'].ReadAsArray( 0, yoff, win_ysize=1 ) # xoff, yoff, win_xsize, win_ysize
    arryStatus = bands['status'].ReadAsArray( 0, yoff, win_ysize=1 )
    arryMin = bands['min'].ReadAsArray( 0, yoff, win_ysize=1 )
    arryMean = bands['mean'].ReadAsArray( 0, yoff, win_ysize=1 )
    arryMax = bands['max'].ReadAsArray( 0, yoff, win_ysize=1 )
    
    result = { v: setClassMap( v ) for v in class_map }
    del arryMap, arryStatus, arryMin, arryMean, arryMax
    return result

def groupStatistic(group, elem):
    """
    group/elem = { class_map_1: { neg: { count, min, max, mean_sum }, pos: { count, max, mean_sum } }, class_map_2, ... }
    """
    def setGroupMinMax(id_map, tend, value):
        cmpValue = lambda g, e: g > e # Minimum - 'min'
        if value.find('max') > -1: # Maximum - 'max'
            cmpValue = lambda g, e: g < e
        if group[ id_map][ tend ][ value ]:
            if elem[ id_map][ tend ][ value ] and cmpValue( group[ id_map][ tend ][ value ], elem[ id_map][ tend ][ value ] ):
                group[ id_map][ tend ][ value ] = elem[ id_map][ tend ][ value ]
            return
        if elem[ id_map][ tend ][ value ]:
            group[ id_map][ tend ][ value ] = elem[ id_map][ tend ][ value ]

    for id_map in group.keys():
        for tend in ('neg', 'pos'):
            group[ id_map ][ tend]['count'] += elem[ id_map ][ tend ]['count']
            group[ id_map ][ tend]['mean_sum'] += elem[ id_map ][ tend ]['mean_sum']
            setGroupMinMax(id_map, tend, 'min')
            setGroupMinMax(id_map, tend, 'max')

def printStatistic(statistic, id_map, legend):
    print(f"Tendencia - {legend[ id_map ]}:")
    for k, v in { 'neg': 'Negativa', 'pos': 'Positiva'}.items():
        values = [ f"{s}: {str( statistic[ id_map ][ k ][ s ] )}" for s in ('count', 'min', 'mean', 'max') ]
        values = ",".join( values )
        print( f". {v} -> {values}")

def run(filename, level):
    """
    Bands: 1.Mapbiomas .min, 3.mean, 4.max, 5.count, 6.Status(1:CER,2:NEG,3:NONE,4:POS,5:ALT)
    
    1.Mapbiomas (1o level):
        3 Antrópico
        4 Natural
    OR
    1.Mapbiomas(2o level)
        3 Antrópico
        4 Natural
        5 agriculture
        6 pasture
        7 forest
        8 savana
    """
    class_levels = { 3: 'antropico', 4: 'natural' }
    if level > 1:
        class_levels.update( { 5: 'agricultura', 6: 'pastagem', 7: 'floresta', 8:'savana' } )
    class_map = list( class_levels.keys() )

    ds = gdal.Open( filename, GA_ReadOnly )
    bands = ( 'map', 'min', 'mean', 'max', 'count', 'status' )
    bands = { bands[ idx ]: ds.GetRasterBand( idx+1 ) for idx in range( len( bands) ) }
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    statistic = getStatistic( class_map, bands, 0, xsize )
    for y in range( 1, ysize):
        printProgressBar(y + 1, ysize, prefix=filename, suffix='Complete', length = 50)
        r = getStatistic( class_map, bands, y, xsize )
        groupStatistic( statistic, r )
    ds = None
    
    for id_map in statistic.keys():
        for tend in ( 'neg', 'pos'):
            statistic[ id_map ][ tend ]['mean' ] = None if not statistic[ id_map ][ tend ]['count'] \
                else statistic[ id_map ][ tend ]['mean_sum'] / statistic[ id_map ][ tend ]['count']
        printStatistic( statistic, id_map, class_levels )

def main():
    parser = argparse.ArgumentParser(description=f"Get values MIN, MEAN, MAX of tends(POS and NEG) for Mapbiomas class." )
    parser.add_argument( 'filename', action='store', help='File name of MIN MEAN MAX(Ex.: cerrado_mapbioma_tend_min-mean-max.tif)', type=str)
    parser.add_argument( 'level', action='store', help='Level of image(1: *_mapbioma_*,2:*_mapbioma_agr_pas_for_sav_*)', type=int)

    args = parser.parse_args()
    return run( args.filename, args.level )

if __name__ == "__main__":
    sys.exit( main() )
