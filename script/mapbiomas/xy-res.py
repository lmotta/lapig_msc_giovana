#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : X Y Resolution
Description          : Get X and Y resolution
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
__date__ = '2020-08-28'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'
 
import sys, os
import argparse
from osgeo import gdal


gdal.AllRegister()

def run(image):
    def existsFile(image):
        if not os.path.isfile( image ):
            msg = f"Missing image {image}"
            print( msg )
            return False
        return True
    # Check
    if not existsFile( image ):
        return 1
    
    # Origin
    ds = gdal.Open( image, gdal.GA_ReadOnly )
    ( ulXOrigin, resX, rotX, ulYOrigin, rotY, resY ) = ds.GetGeoTransform()
    ds = None
    msg = f"{resX} {resY}"
    print(msg)

    return 0

def main():
    parser = argparse.ArgumentParser(description=f"Get X and Y resolution." )
    parser.add_argument( 'image', action='store', help='Image', type=str)
    
    args = parser.parse_args()
    return run( args.image)

if __name__ == "__main__":
    sys.exit( main() )
