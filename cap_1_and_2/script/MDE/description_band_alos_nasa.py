 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, argparse
from osgeo import gdal, gdalconst

def descriptionBands( filepath):
    names =  ('alos', 'nasa')
    ds = gdal.Open( filepath, gdalconst.GA_Update )
    for index,name in enumerate( names ):
        n_band = index + 1
        band = ds.GetRasterBand( n_band )
        band.SetDescription( name )
        ds.FlushCache()
        band = None
    ds = None

def main():
    parser = argparse.ArgumentParser(description='Add description Alos and Nasa in Bands.')
    parser.add_argument( 'filepath', action='store', help='Filepath of alos_nasa.tif', type=str)
    args = parser.parse_args()
    return descriptionBands( args.filepath )

if __name__ == "__main__":
    sys.exit( main() )