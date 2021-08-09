#!/bin/bash
#
# ***************************************************************************
# Name                 : GPM Nasa Month Clip
# Description          : Clip  Nasa Monthimages with shapefile
# Arguments            : Nasa Month directory and shapefile 
# Dependencies         : None
#
#                       -------------------
# begin                : 2021-06-19
# copyright            : (C) 2021 by Luiz Motta
# email                : motta dot luiz at gmail.com
# ***************************************************************************
# 
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************
#
#
name_script=$(basename $0)
if [ $# -ne 3 ] ; then
  echo "Usage: $name_script <directory> <shapefile> <out_prefix>" >&2
  echo "<directory> is the directory of 3B-MO-GIS.MS.MRG.3IMERG.*.total.accum images(*.tif)" >&2
  echo "<shapefile> is the shapefile(.shp)" >&2
  echo "<out_prefix> is the preffix for output image" >&2
  exit 1
fi
#
# Input file:  3B-MO-GIS.MS.MRG.3IMERG.20000601-S000000-E235959.06.V06B.total.accum.tif
# Output file: out_prefix_aaaa_mm_total.accum.tif
#
dir=$1
shp=$2
pref=$3
#
suf='total.accum.tif'
#
for f in $(ls $(echo $dir"/*."$suf) )
do
    fn=$(basename $f .tif)
    v_date=$(echo $fn | cut -d'.' -f5 | cut -d'-' -f1)
    aaaa=$(echo $v_date | cut -c -4)
    mm=$(echo $v_date | cut -c 5-6)
    fn=$pref"_"$aaaa"_"$mm"_"$suf
    echo $fn
    gdalwarp -q -t_srs EPSG:4326 -of 'Gtiff' -nomd -overwrite -dstnodata 29999 -cutline  $shp $f -cblend 0.5 $fn
done
