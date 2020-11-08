#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import glob
import csv
import argparse

def getNameCsv(pathfile):
    return pathfile.split( os.path.sep )[-1][:-4]


class InmetCsv():
    HEADERSTATION = (
        'source', 'source_ano',
        'regiao', 'uf',
        'estacao', 'code_wmo',
        'lat', 'long', 'alt',
        'data'
    )
    HEADERTABLE = (
        'source', 'code_wmo',
        'data', 'hora',
        'prep_mm',
        'pres_mb', 'pres_max_mb', 'pres_min_mb',
        'rad_wm2',
        'temp_bulbo_c', 'temp_pont_orv_c', 'temp_max_c', 'temp_min_c',
        'temp_orv_max_c', 'temp_orv_min_c',
        'umid_max_p', 'umid_min_p', 'umid_p',
        'vent_dir_g', 'vent_max_ms', 'vent_vel_ms'
    )
    SEP_CSV = ';'
    def __init__(self, csv_station, csv_table):
        self.csv_station = open( csv_station, mode='w' )
        header = f"{self.SEP_CSV.join( self.HEADERSTATION )}\n"
        self.csv_station.write( header )

        self.csv_table = open( csv_table, mode='w' )
        header = f"{self.SEP_CSV.join( self.HEADERTABLE )}\n"
        self.csv_table.write( header )

    def __del__(self):
        self.csv_station.close()
        self.csv_table.close()

    def addRows(self, pathfile):
        srcName = getNameCsv( pathfile )
        srcYear = srcName.split('_')[-1].split('-')[-1]
        # CSV - number = D,D
        with open( pathfile, mode='r', errors="surrogateescape") as f:
            lines = f.readlines()
        #
        # Station
        rows = len( self.HEADERSTATION ) - 2
        f_value = lambda l: l.strip().split(self.SEP_CSV)[1].replace(',', '.')
        values = [ f_value( l ) for l in lines[ :rows ] ]
        values = [ srcName, srcYear ] + values
        w_line = f"{self.SEP_CSV.join( values )}\n"
        self.csv_station.write( w_line )
        code_wmo = values[ self.HEADERSTATION.index('code_wmo') ]
        # Table
        del lines[: rows + 1]
        columns = len( self.HEADERTABLE ) - 2
        w_lines = []
        for line in lines:
            values = [ v.replace(',', '.') for v in line.strip().split( self.SEP_CSV ) ]
            del values[ columns: ]
            values = [ srcName, code_wmo ] + values
            w_line = f"{self.SEP_CSV.join( values )}"
            w_lines.append( w_line )
        self.csv_table.write( "\n".join( w_lines ) )
        self.csv_table.write('\n')
        del w_lines[:]
        del values[:]

def printStatus(message, newLine=False):
    ch = '\n' if newLine else ''
    sys.stdout.write( "\r{}".format( message.ljust(100) + ch ) )
    sys.stdout.flush()

def run(dir_csv):
    ext_csv = 'CSV'
    csv_station = os.path.join( dir_csv, 'stations.csv' )
    csv_table = os.path.join( dir_csv,'stations_table.csv' )
    ic = InmetCsv( csv_station, csv_table )
    l_csv = [ f for f in glob.glob(f"{dir_csv}{os.path.sep}*.{ext_csv}") ]
    count, total = 1, len( l_csv)
    for csv in l_csv:
        name = getNameCsv( csv )
        msg = f"{count}/{total}: {name}"
        printStatus( msg )
        count += 1
        ic.addRows( csv )
    del ic
    return 0

def main():
    msg = "Create CVS's tables from Inmet CSVs Directory."
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('dir_csv', type=str, help='CSVs Directory')

    args = parser.parse_args()
    
    if not os.path.isdir( args.dir_csv ):
        msg = f"'{args.dir_csv}' is missing"
        printStatus( msg, True )
        return 1
    return run( args.dir_csv )

if __name__ == '__main__':
    sys.exit( main() )

#dir_csv = '/home/lmotta/data/giovana/inmet_estacoes/csv'
