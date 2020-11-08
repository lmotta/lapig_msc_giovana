#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import os, sys, glob, argparse

def printStatus(message, newLine=False):
    ch = '\n' if newLine else ''
    sys.stdout.write( "\r{}".format( message.ljust(100) + ch ) )
    sys.stdout.flush()

def getDescribeArea(f_csv, header, area_pixel):
    name = f_csv.split( os.path.sep )[-1].split('.')[0]
    df = pd.read_csv( f_csv, skiprows=1, names=header )
    desc = df.describe()
    area = desc['AW3D30']['count'] * area_pixel
    desc = str( desc )
    df = None
    
    return ( desc, area )

def saveInfo(name, describe, area):
    with open( f"{name}.info", 'w') as f:
        f.write( f"{name}\n\n")
        f.write( f"{describe}\n\n" )
        f.write( f"Area = {area}\n")

def run(dir_csv):
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    header = ['AW3D30', 'NASADEM']
    area_pixel = 900
    
    l_csv = [ f for f in glob.glob(f"{dir_csv}{os.path.sep}*.csv") ]
    for csv in l_csv:
        name = csv.split( os.path.sep )[-1].split('.')[0]
        msg = f"Saving {name}.info..."
        printStatus( msg )
        ( desc, area) = getDescribeArea( csv, header, area_pixel )
        saveInfo( name, desc, area )
    return 0

def main():
    parser = argparse.ArgumentParser(description='Create Infofiles from CSVs Directory.')
    parser.add_argument('dir_csv', type=str, help='CSVs Directory')
    args = parser.parse_args()
    
    if not os.path.isdir( args.dir_csv ):
        msg = f"'{args.dir_csv}' is missing"
        printStatus( msg, True )
        return 1
    return run( args.dir_csv )

if __name__ == '__main__':
    sys.exit( main() )

#dir_csv = '/home/lmotta/data/giovana/bd_gis/mapbiomas_dem_csv'
