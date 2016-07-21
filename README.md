# landuse
Landuse and patten recognition project

This is a set of scripts to perform land use classification on multi-spectral aerial imagery. 

##Usage##

Necessary libraries: GDAL, Spectral Python, Numpy, Python Imaging Library

The first step is to group all of the individual band images from the Landsat level 1 product into one multiband tif. This should be done with the gdal_merge.py script with the following syntax

gdal_merge.py -seperate -v band1img_path band2img_path band3img_path band4img_path ...

This will create a file "out.tif" with all of the bands merged into it. This file can be used with the python script.

To use process_v1.py the user must open the script and modify the paths to the source raster (out.tif) and classified images. The user must also make arrays in the section under the path specification section that reflect the classificaions of their sample images. I have been choosing sample images of entirely the same subject so far, so that the classification array needed for them is just filled with a single number, and can be created by "namemsk = np.zeros((rows,columns)) + index". Additionally the number of bands in the source raster and classified images must be specified and equal right now. Once all of the user defined variables are set up the script can be run with the syntax

python process_v1.py

and will produce the output tiffs "kclimg.tif" from the k-means unsupervised classification, "gclimg.tif" from the Gaussian maximum likelihood supervised classification, and "mclimg.tif" from the Mahalanobis distance supervised classification.

The analyzate.sh script will takes the path to a folder with the band images, the process_vbash.py script, and the gdal_merge.py script as an argument and automates the process. It is buggy sometimes though. Usage is like this:

./analyzate.sh /path/to/image/and/script/directory

The script will not work if the process_vbash.py and gdal_merge.py scripts are not in the given directory along with the images.

