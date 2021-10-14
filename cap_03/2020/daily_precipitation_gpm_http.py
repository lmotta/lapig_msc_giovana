#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Daily precipitation GPM
Description          : Create a CSV file with values of daily precipitation
                       from HTTPS (jsimpsonhttps.pps.eosdis.nasa.gov)
                       - CSV Fields:  ID station | date | total_mm(APD)
                       - APD (Accumulation Precipitation of Day):
                            Previuos day(12:00 to 23:59) + Current day(00:00 to 11:59)
                       Save CSV in directory where this called
Date                 : March, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

Dependences:
- mod_py

Updates:
- 2020-09-22
. Change host: https://jsimpsonhttps.pps.eosdis.nasa.gov
. Root directory: /imerg/gis
. Date directory: YYYY/mm
. Name: 3B-HHR-L.MS.MRG.3IMERG.20061222-S100000-E102959.0600.V06B.30min.tif

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
__date__ = '2020-03-16'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'
 
import sys, os, csv
from datetime import datetime, timedelta
import urllib.request, urllib.error
from multiprocessing.pool import ThreadPool

from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
gdal.UseExceptions()

from mod_py.valuepixel import ValuePixel

import argparse
from mod_py.argparse_types import DateType, EmailType, FilePathType

def addBasicAuthenticationRequest(host, user, password):
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, host, user, password )
    authhandler = urllib.request.HTTPBasicAuthHandler( passman )
    opener = urllib.request.build_opener( authhandler)
    urllib.request.install_opener(opener)


class GpmDataset():
    HOST = 'jsimpsonhttps.pps.eosdis.nasa.gov'
    TYPE_IMAGE = '3B-HHR-L.MS.MRG.3IMERG'
    DIR = 'imerg/gis'
    VERSION = 6
    RANGE = '30min' 
    CONFIG_TIME = {
        'iniHourBefore': 12,
        'deltaStep': timedelta(minutes=30),
        'deltaSecond': timedelta(seconds=1)
    }
    IMAGES_DAY = 48 # Day(24h) = 48 * 1/2 hour
    VSICURL = False

    @staticmethod
    def formatImageName():
        """
        Example image: 3B-HHR-L.MS.MRG.3IMERG.20061222-S100000-E102959.0600.V06B.30min.tif
        - Type: 3B-HHR-L.MS.MRG.3IMERG
        - Day: 20061222 (YYYYmmDD)
        - Start: S100000 (HHMMSS)
        - End:   E102959 (HHMMSS)
        - Total minutes of day: 0600 (DDDD)
        - Version: V06B (version = 6)
        - Range: 30min

        Usage:
            f_name = formatImageName()
            name = f_name.format( **valueDatetime )

            valueDatetime = {
                'year', 'month', 'day',
                's_hour', 's_minute', 's_second',
                'e_hour', 'e_minute', 'e_second',
                'totalmin'
            }
        """
        f_image = {
            'type': GpmDataset.TYPE_IMAGE,
            'day': '{year:04}{month:02}{day:02}',
            'start': 'S{s_hour:02}{s_minute:02}{s_second:02}',
            'end': 'E{e_hour:02}{e_minute:02}{e_second:02}',
            'totalmin': '{totalmin:04}',
            'version': f"V{GpmDataset.VERSION:02}B",
            'range': GpmDataset.RANGE
        }
        return "{type}.{day}-{start}-{end}.{totalmin}.{version}.{range}".format( **f_image )

    @staticmethod
    def getValuesDatatime(v_datetime):
        """
        Args:
            v_datetime: datetime
        Return: Generator of dictionary of valueDatetime(see formatImageName )
                Previuos day(12:00 to 23:59) and Current day(00:00 to 11:59)
        """
        previosDay = v_datetime - timedelta(days=1)
        args = ( previosDay.year, previosDay.month, previosDay.day, GpmDataset.CONFIG_TIME['iniHourBefore'] )
        s_dt = datetime( *args )
        for _i in range( GpmDataset.IMAGES_DAY ):
            e_dt = s_dt + GpmDataset.CONFIG_TIME['deltaStep'] - GpmDataset.CONFIG_TIME['deltaSecond']
            v = {
                'year': s_dt.year,
                'month': s_dt.month,
                'day': s_dt.day,
                's_hour': s_dt.hour,
                's_minute': s_dt.minute,
                's_second': s_dt.second,
                'e_hour': e_dt.hour,
                'e_minute': e_dt.minute,
                'e_second': e_dt.second,
                'totalmin': s_dt.hour * 60 + s_dt.minute
            }
            s_dt += GpmDataset.CONFIG_TIME['deltaStep']
            yield v

    def __init__(self, email):
        addBasicAuthenticationRequest( f"https://{self.HOST}", email, email )
        f_image = {
            'root': f"https://{self.HOST}/{self.DIR}",
            'dir': '{year:04}/{month:02}',
            'name': self.formatImageName()
        }
        self.host_image = "{root}/{dir}/{name}.tif".format( **f_image )
        self.getDS = self._getDS_Vsicurl if self.VSICURL else self._getDS_Download
        
    def isLive(self, v_datetime):
        """
        Args:
            v_datetime: datetime
        """
        valueDatetime = {
            'year': v_datetime.year, 'month': v_datetime.month, 'day': v_datetime.day,
            'e_hour': 12, 'e_minute': 29, 'e_second': 59,
            's_hour': 12, 's_minute': 0,  's_second': 0,
            'totalmin': 720
        }
        url = self.host_image.format( **valueDatetime )
        try:
            _response = urllib.request.urlopen(url, timeout=5)
        except urllib.error.URLError as e:
            return { 'isOk': False, 'message': f"Host: '{self.HOST}'\nUrl: {url}\n{e.reason}" }
        
        return { 'isOk': True }

    def _getDS_Vsicurl(self, url):
        ds = None
        url = f"/vsicurl/{url}"
        try:
            ds = gdal.Open( url, GA_ReadOnly )
        except RuntimeError: # gdal
            msg = f"Url '{url}': Error open image"
            return { 'isOk': False, 'message': msg }
        return { 'isOk': True, 'dataset': ds }

    def _getDS_Download(self, url):
        ds = None
        image = url.split('/')[-1]
        try:
            if not os.path.exists( image ):
                _response = urllib.request.urlopen(url, timeout=5) # Check if can access
                urllib.request.urlretrieve( url, image )
            ds = gdal.Open( image, GA_ReadOnly )
        except urllib.error.URLError as e: # urllib
            msg = f"Url '{url}': n{e.reason}"
            return { 'isOk': False, 'message': msg }
        except RuntimeError: # gdal
            os.remove( image )
            msg = f"Url '{url}': Error open image"
            return { 'isOk': False, 'message': msg }
        return { 'isOk': True, 'dataset': ds }

    def __call__(self, valueDatetime):
        url = self.host_image.format( **valueDatetime )
        return self.getDS( url )


def saveCsvDailyGpm(dateIni, dateEnd, pathfileCoordCsv, getDataSetGpm, download_keep, printStatus):
    def getStationsCsv(filepath):
        item = lambda row: {
            'id': row[0],
            'lat': float( row[1] ), 'long': float( row[2] )
        }
        with open( filepath) as csvfile:
            rows = csv.reader( csvfile, delimiter=SEP_CSV )
            next( rows )
            stations = [ item( row ) for row in rows ]
        return stations

    def createWriteFile(filepath, head=None):
        csvfile = open( filepath, mode='w')
        writer = csv.writer( csvfile, delimiter=SEP_CSV )
        if head: writer.writerow( head )
        return { 'csvfile': csvfile, 'writerows': writer.writerows }

    def getTotalPrecipitation(v_datetime, labelDate):
        """
        return: { 'stations_total', 'errors' }
        """
        def getDatasetSources():
            f_name = GpmDataset.formatImageName()
            c_images = 0
            sources, errors = [], []
            for vd in GpmDataset.getValuesDatatime( v_datetime ):
                c_images += 1
                name = f_name.format( **vd )
                msg = f"{labelDate} - Fetching {name} ({c_images}/{GpmDataset.IMAGES_DAY})..."
                printStatus( msg )
                r = getDataSetGpm( vd )
                sources.append( r['dataset'].GetDescription() ) if r['isOk'] else errors.append( r['message'] )

            return { 'sources': sources, 'errors': errors }

        def getStationsPrecipitations(source):
            """
            Args:
                source: Source of Dataset
            """
            ds = gdal.Open( source, GA_ReadOnly )
            vp = ValuePixel( ds )
            vp.setBand(1)
            item = lambda s: ( s['id'], vp( s['long'], s['lat'] ) )
            station_precipitation = [ item( s ) for s in stations ]
            ds = None

            return station_precipitation
        
        r = getDatasetSources()
        sources = r['sources']
        errors = r['errors']

        msg = f"{labelDate} - Precipitations calculating..."
        printStatus( msg )
        pool = ThreadPool(processes=4)
        mapResult = pool.map_async( getStationsPrecipitations, sources )
        stations_total = { k['id']: 0 for k in stations }
        for results in mapResult.get():
            for k,v in results: stations_total[ k ] += v
        pool.close()
        if not download_keep:
            for src in sources: os.remove( src )
        sources.clear()
        return { 'stations_total': stations_total, 'errors': errors }

    SEP_CSV = ';'
    FACTOR_MM_DAY = 10
    
    stations = getStationsCsv(pathfileCoordCsv) # [ { 'id', 'lat', 'long' }, ... ]

    suffix = f"{dateIni.strftime('%Y-%m-%d')}_{dateEnd.strftime('%Y-%m-%d')}"
    name = os.path.splitext( os.path.basename( pathfileCoordCsv ) )[0]
    name = f"{name}_daily_precip_{suffix}"
    filePathOut = f"{name}.csv"
    fwOut = createWriteFile( filePathOut, ['id', 'date', 'total_mm'] )

    filePathError = f"{name}_error.csv"
    fwError = createWriteFile( filePathError, ['date', 'message'] )
    totalError = 0
    
    delta = dateEnd - dateIni
    totalDays = delta.days + 1
    msg = f"{totalDays} Days | {GpmDataset.IMAGES_DAY} Images/Day | {len( stations )} Stations"
    print( msg )
    c_days = 0
    try:
        for d in range( totalDays ):
            dt = ( dateIni + timedelta(days=d) )
            c_days += 1
            labelDate = dt.strftime('%Y-%m-%d')
            label = f"{labelDate} ({c_days}/{totalDays})"
            r  = getTotalPrecipitation( dt, label)
            if r['errors']:
                totalError += len( r['errors'] )
                items = ( [ labelDate, error ] for error in r['errors'] )
                fwError['writerows']( items )
                fwError['csvfile'].flush()
            items = ( [ k, labelDate, v/FACTOR_MM_DAY ] for k, v in r['stations_total'].items() )
            fwOut['writerows']( items )
            fwOut['csvfile'].flush()
    except Exception as e:
        print(f"\nError processing: {str(e)}\n")
    fwOut['csvfile'].close()
    fwError['csvfile'].close()
    msg = f"Saved '{filePathOut}'."
    printStatus( msg )
    if not totalError:
        os.remove( filePathError )
    else:
        msg = f"\nErrors read images ({totalError} images): '{filePathError}'\r"
        print( msg )


def run(email, ini_date, end_date, filepath_csv, download_keep):
    def printStatus(message):
        msg = f"\r{message.ljust(100)}"
        sys.stdout.write( msg )
        sys.stdout.flush()

    def messageDiffDateTime(dt1, dt2):
        diff = dt2 - dt1
        return "Days = {} hours = {}".format( diff.days, diff.seconds / 3600 )

    if ini_date > end_date:
        lblIni = ini_date.strftime('%Y-%m-%d')
        lblEnd = end_date.strftime('%Y-%m-%d')
        msg = f"ini_date({lblIni}) > end_date({lblEnd})"
        print( msg )
        return 0

    gpmDS = GpmDataset( email )
    r = gpmDS.isLive( ini_date )
    if not r['isOk']:
        print( r['message'])
        return 0

    dtIni = datetime.now()
    print('Started ', dtIni)

    saveCsvDailyGpm(ini_date, end_date, filepath_csv, gpmDS, download_keep, printStatus )
    
    dtEnd = datetime.now()
    msgDiff = messageDiffDateTime( dtIni, dtEnd )
    print('\nFinished ', f"{dtEnd}({msgDiff})")
    return 0

def main():
    parser = argparse.ArgumentParser(description=f"Create precipitation daily from NASA/GPM ({GpmDataset.HOST})." )
    parser.add_argument( 'email', action='store', help='Email user for NASA/GPM', type=EmailType('RFC5322') )
    parser.add_argument( 'ini_date', action='store', help='Initial date (YYYY-mm-DD)', type=DateType() )
    parser.add_argument( 'end_date', action='store', help='End date (YYYY-mm-DD)', type=DateType() )
    parser.add_argument( 'filepath_csv', action='store', help='Filepath of CSV with coordinates of stations', type=FilePathType() )
    parser.add_argument( '-d', '--download_keep', action="store_true", help='Keep downloads')

    args = parser.parse_args()
    return run( args.email, args.ini_date, args.end_date, args.filepath_csv, args.download_keep )

if __name__ == "__main__":
    sys.exit( main() )
