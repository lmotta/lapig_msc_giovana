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

from osgeo import gdal
from gdalconst import GA_Update

gdal.UseExceptions()
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.SetCacheMax (1000000000)


def run(filename, n_band, description):
    ds = gdal.Open( filename, GA_Update )
    b = ds.GetRasterBand( n_band )
    b.SetDescription( description )
    b.FlushCache()
    ds = None

def main():
    parser = argparse.ArgumentParser(description=f"Add description in band." )
    parser.add_argument( 'filename', action='store', help='File name of image', type=str)
    parser.add_argument( 'n_band', action='store', help='Number of band', type=int)
    parser.add_argument( 'description', action='store', help='Band description ', type=str)

    args = parser.parse_args()
    return run( args.filename, args.n_band, args.description)

if __name__ == "__main__":
    sys.exit( main() )

