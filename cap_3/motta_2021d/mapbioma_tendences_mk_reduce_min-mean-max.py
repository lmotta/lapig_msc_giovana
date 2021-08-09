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

from osgeo import gdal
from gdalconst import GA_ReadOnly

gdal.UseExceptions()
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.SetCacheMax (1000000000)


class ValueBand():
    struct_types = {
        gdal.GDT_Byte: 'B',
        gdal.GDT_UInt16: 'H',
        gdal.GDT_Int16: 'h',
        gdal.GDT_UInt32: 'I',
        gdal.GDT_Int32: 'i',
        gdal.GDT_Float32: 'f',
        gdal.GDT_Float64: 'd'
    }
    def __init__(self, ds):
        self.ds = ds
        band = ds.GetRasterBand(1)
        self.nodata = band.GetNoDataValue()
        typeBand = band.DataType
        self.data = { 'xsize': 1, 'ysize': 1, 'buf_type': typeBand }

        transf = ds.GetGeoTransform()
        self.x_min, self.y_max = transf[0], transf[3]
        self.x_max, self.y_min = self.x_min + ds.RasterXSize * transf[1], self.y_max + ds.RasterYSize * transf[-1]
        self.transfInv = gdal.InvGeoTransform( transf )
        self.offsetData = None
        
        self.struct_format = self.struct_types[ typeBand ]
        self.value = lambda unpack_value: unpack_value[0] \
            if typeBand in ( gdal.GDT_Float32, gdal.GDT_Float64 ) \
            else     lambda unpack_value: int( unpack_value[0] )

    def isValid(self, x, y):
        return self.x_min < x < self.x_max and self.y_min < y < self.y_max
        
    def setOffset(self, x, y):
        px, py = gdal.ApplyGeoTransform( self.transfInv, x, y )
        self.offsetData  = dict( { 'xoff': int( px ), 'yoff': int( py ) }, **self.data )

    def getValue(self, n_band):
        struct_value = self.ds.GetRasterBand( n_band ).ReadRaster( **self.offsetData )
        unpack_value = struct.unpack( self.struct_format, struct_value )
        return self.value( unpack_value )


class XYCenter():
    def __init__(self, ds):
        ( self.x0, self.s_x, r_x_, self.y0, r_y_, self.s_y) = ds.GetGeoTransform()
    def get(self, col, row):
        return self.x0 + ( col + 0.5) * self.s_x, self.y0 + ( row + 0.5) * self.s_y


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

def createResultDS(ds_map, ds_reduce, filename ):
    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create(filename, ds_map.RasterXSize, ds_map.RasterYSize, ds_reduce.RasterCount + 1, gdal.GDT_Float32 )
    ds.SetGeoTransform( ds_map.GetGeoTransform() )
    ds.SetSpatialRef( ds_map.GetSpatialRef() )
    nodata =  ds_reduce.GetRasterBand(1).GetNoDataValue()
    # Map -> Band 1
    band = ds.GetRasterBand(1)
    band.SetNoDataValue( nodata )
    desc = ds_map.GetRasterBand(1).GetDescription()
    if desc == '':
        desc = 'Map'
    band.SetDescription( desc )
    # Reduce -> Band 2..N
    for idx in range( ds_reduce.RasterCount ):
        band = ds.GetRasterBand( idx+2 )
        band.SetNoDataValue( nodata )
        desc = ds_reduce.GetRasterBand( idx+1 ).GetDescription()
        if desc == '':
            desc = 'Tendence'
        band.SetDescription( desc )
    return ds

def populateResult(ds_map, ds_reduce, ds_result):
    def process(xoff, yoff, cols, rows):
        arr = band_map.ReadAsArray( xoff, yoff, cols, rows ).astype( np.float32 )
        arr[ arr == nodata_map ] = valueBand.nodata
        isnodata = ( arr == valueBand.nodata )
        if ( isnodata == True ).sum() == ( cols * rows ):
            for b in bands_result:
                b.WriteArray( arr, xoff, yoff ) # NoData
            del arr
            return
        
        # Band 1 = Map Band 
        bands_result[0].WriteArray( arr, xoff, yoff )
        # Band 2 .. N = Reduce Bands

        #arrs = [ arr.copy() ] * valueBand.ds.RasterCount
        shape = tuple( [ valueBand.ds.RasterCount ] + list( arr.shape ) )
        arrs = np.zeros( shape ).astype( np.float32 )
        for idx in range( valueBand.ds.RasterCount):
            arrs[ idx ] = arr.copy()

        y, x = np.where(isnodata == False)
        idxs = list( zip( y, x) )
        for idx in idxs:
            coords = xy_map.get( xoff + idx[1], yoff + idx[0] )
            if not valueBand.isValid( *coords ):
                for idBand in range( valueBand.ds.RasterCount ):
                    arrs[ idBand, idx[0], idx[1] ] = valueBand.nodata
                continue
            valueBand.setOffset( *coords )
            for idBand in range( valueBand.ds.RasterCount ):
                arrs[ idBand, idx[0], idx[1] ] = valueBand.getValue( idBand+1 )
        
        for idBand in range( valueBand.ds.RasterCount ):
            bands_result[ idBand+1 ].WriteArray( arrs[ idBand ], xoff, yoff )
        del arrs
    
    bands_result = [ ds_result.GetRasterBand( idx+1 ) for idx in range( ds_result.RasterCount ) ]
    band_map = ds_map.GetRasterBand(1)
    nodata_map =  band_map.GetNoDataValue()
    valueBand = ValueBand( ds_reduce )
    xy_map = XYCenter( ds_map )
    xsize, ysize = band_map.XSize, band_map.YSize
    block_xsize, block_ysize = band_map.GetBlockSize()
    prefix_pb = f"{os.path.basename( ds_result.GetDescription() )}:"
    for y in range( 0, ysize, block_ysize):
        if y + block_ysize < ysize:
            rows = block_ysize
        else:
            rows = ysize - y
        printProgressBar(y + 1, ysize, prefix = prefix_pb, suffix = 'Complete', length = 50)
        for x in range( 0, xsize, block_xsize):
            if x + block_xsize < xsize:
                cols = block_xsize
            else:
                cols = xsize - x
            process( x, y, cols, rows )
            for band in bands_result:
                band.FlushCache()

def run(filename_map, filename_reduce, filename_result):
    ds_map = gdal.Open( filename_map, GA_ReadOnly )
    ds = gdal.Open( filename_reduce, GA_ReadOnly )
    ds_reduce = gdal.GetDriverByName('MEM').CreateCopy('', ds )
    ds = None
    ds_result = createResultDS( ds_map, ds_reduce, filename_result )
    populateResult( ds_map, ds_reduce, ds_result )
    ds_map, ds_reduce, ds_result = None, None, None
    
def main():
    parser = argparse.ArgumentParser(description=f"Create MapBiomas x Tendences." )
    parser.add_argument( 'filename_map', action='store', help='Image of Mapbiomas(1 band)', type=str)
    parser.add_argument( 'filename_reduce', action='store', help='Image tendences reduce min mean max..(5 bands)', type=str)
    parser.add_argument( 'filename_result', action='store', help='Output image MapBiomas x Tendences', type=str)
    args = parser.parse_args()
    return run( args.filename_map, args.filename_reduce, args.filename_result)

if __name__ == "__main__":
    sys.exit( main() )
