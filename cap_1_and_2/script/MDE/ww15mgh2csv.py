#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WW15MGH.GRD:
                                                         grid spacing
   south        north         west     east           n-s         e-w
   -90.000000   90.000000     .000000  360.000000     .250000     .250000

The coverage of this file is:

90.00 N  +------------------+
        |                  |
        | 15' spacing N/S  |
        |                  |
        |                  |
        | 15' spacing E/W  |
        |                  |
-90.00 N  +------------------+
        0.00 E           360.00 E

1) Block:         20(lines) x 8(colums)
2) Total Groups:   9
3) One coordinate: 1 (360 dd = 0 dd)
Total = 1441 longitutes
"""
import sys, os, math, array, argparse

def printStatus(message, newLine=False):
    ch = '\n' if newLine else ''
    sys.stdout.write( "\r{}".format( message.ljust(100) + ch ) )
    sys.stdout.flush()

def getValues(line):
    values = line.strip().split(' ')
    return [ float( v ) for v in values if v != '' ]

def getParams(line):
    [ south, north, west, east, n_s, e_w] = getValues( line ) # Floats
    t_long = ( east - west ) / e_w + 1
    t_lat = ( north - south ) / n_s + 1
    return ( west, int(t_long), e_w, north, int(t_lat), n_s )

def readHeights(file_read):
    v_heights = array.array('d')
    for line in file_read:
        if len( line ) < 4:
            continue
        values = getValues( line )
        v_heights.extend( values )
    return v_heights

def run(ww15mgh_grd):
    name = ww15mgh_grd.split( os.path.sep )[-1]
    msg = f"Reading {name}..."
    printStatus( msg)
    with open( ww15mgh_grd, 'r') as f:
        line = f.readline() #  Header
        ( ini_long, total_long, delta_long, ini_lat, total_lat, delta_lat ) = getParams( line )
        v_heights = readHeights( f )

    ww15mgh_csv = f"{ww15mgh_grd[:-4]}.csv"
    with open( ww15mgh_csv, 'w') as f:
        f.write("LONG,LAT,HEIGHT\n")
        v_lat = ini_lat
        for id_lat in range( total_lat ):
            v_long = ini_long
            id_lat_offset = id_lat * total_long
            msg = f"Latitude {id_lat + 1} of {total_lat}..."
            printStatus( msg)
            # First value (0 dd) = Last value(360 dd) 
            for id_long in range( total_long-1 ):
                id_height = id_lat_offset + id_long
                c_long = math.fmod( v_long + 180.0 , 360.0 ) - 180.0 if v_long > 180 else v_long
                line = f"{c_long},{v_lat},{v_heights[ id_height ]}\n"
                f.write( line )
                v_long += delta_long # West -> East
            v_lat -= delta_lat # North -> south

    name = ww15mgh_csv.split( os.path.sep )[-1]
    msg = f"Saved {name}"
    printStatus( msg, True)
    return 0

def main():
    parser = argparse.ArgumentParser(description='Create CSV from GRD file.')
    parser.add_argument('ww15mgh_grd', type=str, help='GRD file')
    args = parser.parse_args()
    
    if not os.path.isfile( args.ww15mgh_grd ):
        msg = f"'{args.ww15mgh_grd}' is missing"
        printStatus( msg, True )
        return 1
    return run( args.ww15mgh_grd )

if __name__ == '__main__':
    sys.exit( main() )
    # ww15mgh_grd = '/home/lmotta/data/giovana/ondulacao_geoidal/dados_NGA_WW15MGH/WW15MGH/WW15MGH.GRD'

