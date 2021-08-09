#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Band2Csv
Description          : Create CSV with values of each band in a column
Date                 : August, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

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
__date__ = '2020-08-04'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'
 
import sys, os, csv
import argparse
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly

gdal.UseExceptions()
gdal.AllRegister()

def existsFile(image):
    if not os.path.isfile( image ):
        msg = f"Missing image {image}"
        print( msg )
        return False
    return True

def printStatus(message):
    msg = f"\r{message.ljust(100)}"
    sys.stdout.write( msg )
    sys.stdout.flush()

def getValidPixels(bands, rasterXSize, idLine ):
    """
    For each band:
        - (1) Read ONE line                 -> reshape to array [ rasterXSize, 1 ]
        - (2) Valid: pixels != nodata Array -> reshape to array [ rasterXSize, 1 ]
    Join lines of each band:
        - (3) Append = Array [ rasterXSize, nBands ] 
    Valid:
        (4) Valid for both lines(bands), All values pixels need be valid for same location on band 
        (5) Append = Array [ rasterXSize, nBands ] 
        
    (6) Filter data (Join lines) and reshape for Array[ filter line, nBands ]
    """
    def getDataValid(idb):
        data = bands[ idb ].ReadAsArray(0, idLine, rasterXSize, 1 ).reshape( rasterXSize, 1 ) # (1)
        nodata = bands[ idb ].GetNoDataValue()
        valid = data != int( nodata ) if not nodata is None else np.ones( data.shape, dtype=bool ) # (2)
        return ( data, valid )

    nBands = len( bands )
    ( data, valid ) = getDataValid( 0 )
    if nBands == 1:
        data_valid = data[ valid ]
        return data_valid.reshape( len( data_valid ), 1 ).tolist()
    #
    for idb in range(1, nBands ):
        ( d, v ) = getDataValid( idb )
        data = np.append( data, d, axis=1 ) # (3)
        valid = valid & v # (4)
    # Valid Array (5)
    aryValid = np.append( valid, valid, axis=1 ) # 2 bands
    for idb in range(2, nBands ):
        aryValid = np.append( aryValid, valid, axis=1 )
    # Filter (6), data.shape ( rasterXSize, nBands )
    data_valid = data[ aryValid ] #  Flatting ( valids, )
    return data_valid.reshape( int( data_valid.shape[0] / nBands ), nBands ).tolist()

def run(image):
    # Check
    if not existsFile( image ):
        return 1
    
    # Bands
    ds = gdal.Open( image, gdal.GA_ReadOnly )
    bands = []
    for idBand in range( ds.RasterCount ):
        bands.append( ds.GetRasterBand( idBand+1 ) )

    header = [ f"band{b+1}" for b in range( ds.RasterCount ) ]
    filepathCsv = f"{os.path.splitext(image)[0]}.csv"
    with open( filepathCsv, 'w', newline='') as csvfile:
        writer = csv.writer( csvfile, delimiter=',' )
        writer.writerow( header )
        for y in range(0, ds.RasterYSize ):
            msg = f"Line {y+1} of {ds.RasterYSize}"
            printStatus( msg )
            data = getValidPixels( bands, ds.RasterXSize, y )
            writer.writerows( data )
    
    ds = None # Close datasource
    printStatus( f"Saved {filepathCsv}" )
    print('')

    return 0

def main():
    parser = argparse.ArgumentParser(description='Create CSV with values of each band in a column.')
    parser.add_argument( 'image', action='store', help='Image', type=str)

    args = parser.parse_args()
    return run( args.image )

if __name__ == "__main__":
    sys.exit( main() )
