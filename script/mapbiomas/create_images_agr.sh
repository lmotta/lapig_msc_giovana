#!/bin/bash
#
# ***************************************************************************
# Name                 : Create DEM images with agriculture class 
# Description          : Create DEM images with agriculture class from MapBiomas.
#
# Arguments: 
# $1: Directory with shapefiles
# $2: ALOS image
# $3: NASA image
# $4: MAPBIOMAS image
#
# Dependeces:
# - xy-res.py
#
# Use Python3 
#
# Usage:
# Copy this script and xy-res.py to Work's diretory
#
# ***************************************************************************
# begin                : 2020-08-04 (yyyy-mm-dd)
# copyright            : (C) 2020 by Luiz Motta
# email                : motta dot luiz at gmail.com
# ***************************************************************************
#
# Revisions
#
# 2020-08-28:
# - Add xy-res.py script
# 2020-08-30
# - Update Mapbiomas Collection 5(class)
# 
# ***************************************************************************
#
# Example:
#   sh ./creates_images_agr.sh DIR_shapefiles ALOS_image NASA_image MAPBIOMAS_image
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
## Functions
msg_error(){
  local name_script=$(basename $0)
  echo "Usage: $name_script <DIR shapefiles> <ALOS image> <NASA image> <MAPBIOMAS image>" >&2
  echo ""
  echo "Example: creates_images_agr.sh shapefiles.lst"
  exit 1
}
#
create_image(){
    local shp=$1
    # Clip images
    # Alos
    gdalwarp -q -overwrite -tr $xy_res -tap -cutline $shp_dir"/"$shp".shp" -crop_to_cutline -dstnodata -32768 $alos_img alos_clip.tif
    # Nasa
    gdalwarp -q -overwrite -tr $xy_res -tap -cutline $shp_dir"/"$shp".shp" -crop_to_cutline -dstnodata -32768 $nasa_img nasa_clip.tif
    # Mapbiomas
    gdalwarp -q -overwrite -tr $xy_res -tap -cutline $shp_dir"/"$shp".shp" -crop_to_cutline -dstnodata 0 $mapbiomas_img mapbiomas_clip.tif
    # Agriculture images, Nodata = -32767 (-32768 + 1)
    exp_calc="where(logical_or(logical_or(B==20,B==36),logical_or(B==39,B==41)), A, -32767)"
    gdal_calc.py --quiet -A alos_clip.tif -B mapbiomas_clip.tif --outfile alos_agr.tif --calc="$exp_calc"
    gdal_calc.py --quiet -A nasa_clip.tif -B mapbiomas_clip.tif --outfile nasa_agr.tif --calc="$exp_calc"
    # Stack images
    gdal_merge.py -q -separate -a_nodata -32768 -o $shp"_alos_nasa.tif" alos_clip.tif nasa_clip.tif
    gdal_merge.py -q -separate -a_nodata -32768 -o $shp"_alos_nasa_agr.tif" alos_agr.tif nasa_agr.tif
    # clean
    rm alos_*.tif nasa_*.tif mapbiomas_clip.tif > /dev/null
}
#
totalargs=4
#
if [ $# -ne $totalargs ] ; then
  msg_error
  exit 1
fi
##
shp_dir=$1
alos_img=$2
nasa_img=$3
mapbiomas_img=$4
#
cd $shp_dir
files_lst=$(ls -1 *.shp | sed -e 's/\.shp$//')
cd -
#
xy_res=$(python3 ./xy-res.py $alos_img)
#
for item in $files_lst
do
 echo "Processing "$item"..."
 #
 create_image $item
done
