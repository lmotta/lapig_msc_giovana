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

def run(filename_image, filename_values_legend):
    def process(band, pixel_values, xoff, yoff, cols, rows):
        arry = band.ReadAsArray( xoff, yoff, cols, rows )
        for value in pixel_values:
            pixel_values[ value ] += (arry == value).sum().item()

    def readValuesLegend():
        f = open(filename_values_legend, "r")
        lines = f.readlines()
        f.close()
        return { int( v.split(',')[0] ): v.split(',')[1][:-1] for v in lines }

        
    legend = readValuesLegend()
    pixel_values = { v: 0 for v in legend }

    ds = gdal.Open( filename_image, GA_ReadOnly )
    band = ds.GetRasterBand(1)
    
    xsize, ysize = band.XSize, band.YSize
    block_xsize, block_ysize = band.GetBlockSize()
    for y in range( 0, ysize, block_ysize):
        if y + block_ysize < ysize:
            rows = block_ysize
        else:
            rows = ysize - y
        printProgressBar(y + 1, ysize, prefix = 'Calculanting histogram', suffix = 'Complete', length = 50)
        for x in range( 0, xsize, block_xsize):
            if x + block_xsize < xsize:
                cols = block_xsize
            else:
                cols = xsize - x
            process( band, pixel_values, x, y, cols, rows )

    for value in pixel_values:
        msg = f"{legend[ value ]}: {pixel_values[ value ]}"
        print( msg )

    ds = None

def main():
    parser = argparse.ArgumentParser(description=f"Create MapBiomas x Tendences." )
    parser.add_argument( 'filename_image', action='store', help='Image of values(integer)', type=str)
    parser.add_argument( 'filename_values_legend', action='store', help='CSV with values and legend', type=str)
    args = parser.parse_args()
    return run( args.filename_image, args.filename_values_legend )

if __name__ == "__main__":
    sys.exit( main() )
