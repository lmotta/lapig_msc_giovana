#!/bin/bash
#
# Copy this script and shift_origin.py to ALOS directory(ALPSMLC30_*.tif)
#
# 1) Create  run.sh
for f in $(ls -1 ALPSMLC30_*.tif); do echo "python3 ./shift_origin.py "$f" "$(echo $f | sed -e 's+ALPSMLC30_S0+../NASADEM_HGT/s+g' -e 's/W/w/g' -e 's/_DSM.tif/.hgt/g'); done > run.sh
# 2) Run run.sh
echo "Shifting images..."
sh ./run.sh
# 3) Remove run.sh
rm run.sh
echo "Finished"
