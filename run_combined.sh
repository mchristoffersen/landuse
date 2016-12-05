#!/bin/bash

fend=".tif"

cmd="gdal_merge.py -o $1/out.tif -seperate -v "

for i in $( ls $1/*.TIF ); do
	cmd="$cmd $i"
done

$cmd

py1="$1/out.tif"
py2="$1/classif/"
py3=""
for i in $( ls $py2 ); do
	i=${i%$fend}
	py3="$py3,$i"
done
py3=${py3:1}
py4=7
py5=7

./process_vbash.py $py1 $py2 $py3 $py4 $py5


