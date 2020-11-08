#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Shift origin
Description          : Shitf a image to origin of other
Date                 : July, 2020
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
__date__ = '2020-07-21'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'
 
import sys, os
import argparse
from osgeo import gdal


gdal.AllRegister()

def run(shift_image, origin_image):
    def existsFile(image):
        if not os.path.isfile( image ):
            msg = f"Missing image {image}"
            print( msg )
            return False
        return True
    # Check
    if not existsFile( shift_image ) or not existsFile( origin_image ):
        return 1
    
    # Origin
    ds = gdal.Open( origin_image, gdal.GA_ReadOnly )
    ( ulXOrigin, resX, rotX, ulYOrigin, rotY, resY ) = ds.GetGeoTransform()
    ds = None
    # Shift: Update
    ds = gdal.Open( shift_image, gdal.GA_Update )
    ( _ulX, resX, rotX, _ulY, rotY, resY ) = ds.GetGeoTransform()
    params = [ ulXOrigin, resX, rotX, ulYOrigin, rotY, resY ]
    ds.SetGeoTransform( params )
    ds = None

    return 0

def main():
    parser = argparse.ArgumentParser(description=f"Align(shift) a image from origin." )
    parser.add_argument( 'shift_image', action='store', help='Image 1', type=str)
    parser.add_argument( 'origin_image', action='store', help='Image 2', type=str)

    args = parser.parse_args()
    return run( args.shift_image, args.origin_image )

if __name__ == "__main__":
    sys.exit( main() )
