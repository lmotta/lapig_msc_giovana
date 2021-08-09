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

import sys, os, csv, glob, argparse

from osgeo import gdal
from gdalconst import GA_ReadOnly

def getBandsStatistic(filename, n_stat):
    ds = gdal.Open( filename, GA_ReadOnly )
    bands_stat = []
    for idx in range( ds.RasterCount ):
        band = ds.GetRasterBand( idx+1 )
        value = band.GetStatistics(True, True)[ n_stat-1 ]
        bands_stat.append( value )
    ds = None
    return bands_stat

def process(images_dir, prefix_img, n_stat):
    def saveCSV(filename, months, minYear, maxYear ):
        with open( filename, 'w' ) as f:
            writer = csv.writer( f )
            header = [ 'months' ] + [ str( y ) for y in range(minYear, maxYear+1) ]
            writer.writerow( header )
            for m in months:
                values = []
                for y in range(minYear, maxYear+1):
                    v = str( months[ m ][ y ] ) if y in months[ m ] else ''
                    values.append( v )
                row = [ str( m ) ] + values
                writer.writerow( row )

    months = {}
    for y in range(12):
        months[y+1] = {}
    suffix = 'total.accum'
    name = f"{prefix_img}_*_*_{suffix}.tif" # cerrado_2000_06_total.accum.tif
    filter = os.path.join( images_dir, name )
    filenames = sorted( glob.glob( filter ) )
    total_images = len( filenames )
    print(f"{prefix_img} ( {total_images} images)...")

    minYear, maxYear = None, None
    for f in filenames:
        y, m = [ int(v) for v in f.split('_')[1:3] ]
        if minYear is None or y < minYear:
            minYear = y
        if maxYear is None or y > maxYear:
            maxYear = y
        months[ m ][ y ] = getBandsStatistic( f, n_stat )[0]

    f_csv = f"{prefix_img}_{suffix}_stats.csv"
    saveCSV( f_csv, months, minYear, maxYear )
        
gdal.AllRegister()
gdal.UseExceptions()

def run(images_dir, prefix_img, n_stat):
    process( images_dir, prefix_img, n_stat )

def main():
    parser = argparse.ArgumentParser(description='Create statistics from GPM Nasa.' )
    parser.add_argument( 'images_dir', action='store', help='Directory with images', type=str)
    parser.add_argument( 'prefix_img', action='store', help='Prefix of images(ex.:cerrado_2000_06_total.accum.tif)', type=str)
    parser.add_argument( 'n_stat', action='store', help='1: Min, 2: Max 3: Mean', type=int)

    args = parser.parse_args()
    return run( args.images_dir, args.prefix_img, args.n_stat )

if __name__ == "__main__":
    sys.exit( main() )
