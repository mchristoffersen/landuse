# landuse
Landuse and patten recognition project

This is code written to run automatic classifiers on multiband rasters.

[![DOI](https://zenodo.org/badge/63271494.svg)](https://zenodo.org/badge/latestdoi/63271494)

##Usage##

Necessary libraries: GDAL, Spectral Python, Numpy, Python Imaging Library

This script will take a multiband raster and a set of training images as input, and output images classified with Mahalanobis, Gaussian, and K-Means classifiers. 

The first step is to group all of the individual band images from the Landsat level 1 product into one multiband tif. This should be done with the included gdal_merge.py script with the following syntax

gdal_merge.py -o output.tif -seperate -v band1img_path band2img_path band3img_path band4img_path ...

Here is what is needed to merge the example data:

gdal_merge.py -o ./sample_input/output.tif -seperate -v ./sample_input/LM50270391984196AAA03_B1.TIF ./sample_input/LM50270391984196AAA03_B2.TIF ./sample_input/LM50270391984196AAA03_B3.TIF ./sample_input/LM50270391984196AAA03_B4.TIF

This will create a file "output.tif" with all of the bands merged into it. This file can be used with the python script.

Next you will need to open "output.tif" in your favorite GIS and crop out homogenous (in terms of feature type) sections of the image. This is for the trained classifiers. Next make a file in the format of "./sample_input/training.txt" - a file path and an integer "class" to associate with the training data in that file. The integers must start from 1.

To run the classification, call the classify.py script with the data raster and training image text file as arguments:

python ./sample_input/output.tif ./sample_input/training.txt

The script will run and save an image for each classification.

Coming soon:
Georeferenced output
Getting rid of Spectral Python (seems to be dead) probably replacing it with scikit-learn
Better documentation
