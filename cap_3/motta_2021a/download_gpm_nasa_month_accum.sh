#!/bin/bash
#
# ***************************************************************************
# Name                 : Download gpm nasa month accum Image
# Description          : Download month..total.accum.tif
# Arguments            : Email Year Month_Ini Month_End
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
if [ $# -ne 4 ] ; then
  echo "Usage: $name_script <email> <year> <month_ini> <month_end>" >&2
  echo "<email> is the email for arthurhouhttps.pps.eosdis.nasa.gov" >&2
  echo "<year> is year with 4 digit(Ex.: 2001) start from 2000" >&2
  echo "<month_ini> is the start month with 2 digit. For 200 start from 06" >&2
  echo "<month_ini> is the end month with 2 digit" >&2
  exit 1
fi
#
#
email=$1
aaaa=$(printf "%04d" $2)
month_ini=$3
month_end=$4
#
prefix_server=https://arthurhouhttps.pps.eosdis.nasa.gov/gpmdata
#
for v in $(seq $month_ini $month_end)
do
    mm=$(printf "%02d" $v)
    f_tif="3B-MO-GIS.MS.MRG.3IMERG."$aaaa""$mm"01-S000000-E235959."$mm".V06B.total.accum.tif"
    echo "Download "$f_tif
    curl -sO -u $email":"$email $prefix_server"/"$aaaa"/"$mm"/01/gis/3B-MO-GIS.MS.MRG.3IMERG."$aaaa""$mm"01-S000000-E235959."$mm".V06B.zip"
    f_zip="3B-MO-GIS.MS.MRG.3IMERG."$aaaa""$mm"01-S000000-E235959."$mm".V06B.zip"
    unzip -q $f_zip $f_tif
    rm $f_zip
done
