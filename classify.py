# Michael Christoffersen

# Script to perform supervised and unsupervised classification on
# multiband rasters, probably best used as a template for your own
# specific purpose

# Python 2.7
# GDAL ...
# Numpy ...
# SpectralPy ...
# PIL ...

from osgeo import gdal
from gdalconst import *
import numpy as np
import spectral as sp
from PIL import Image
import sys

## Params
kmeans_iterations = 10
kmeans_clusters = 8
##

data_path = sys.argv[1] # Path the the multiband raster
tlist_path = sys.argv[2] # Path to the training dataset CSV
out_path = './'

# Open the data raster
data_f = gdal.Open(data_path, GA_ReadOnly)
data_nband = data_f.RasterCount

# Open the training images
tlist_f = open(tlist_path, 'r')
tlist = tlist_f.read()
tlist = filter(None,tlist.split('\n')) # make a list of lines, filter out empty ones
tlist = [line.split(',') for line in tlist]

trefs = [None]*len(tlist) # to hold training image file refs

maxy = -1
sumx = 0
for i in range(len(tlist)):
	trefs[i] = gdal.Open(tlist[i][0], GA_ReadOnly)
	
	maxy = max(maxy, trefs[i].RasterYSize)
	sumx = sumx + trefs[i].RasterXSize
	
	if(trefs[i].RasterCount != data_nband):
	  out_msg = "Training image " + tlist[i] + " has invalid number of bands (" + str(trefs[i].RasterCount) + ").\nNumber of bands must equal data (" + str(data_nband) + ")." 
	  sys.stderr.write(out_msg)
	  sys.exit()
	 
# Create training array
tdata = np.zeros((maxy, sumx, data_nband))
tmask = np.zeros((maxy, sumx))

xpos = 0
for i in range(len(trefs)):
  xs = trefs[i].RasterXSize
  ys = trefs[i].RasterYSize
  tmask[0:ys, xpos:xpos+xs] = int(tlist[i][1])
  for j in range(data_nband):
    tdata[0:ys, xpos:xpos+xs, j] = trefs[i].GetRasterBand(j+1).ReadAsArray()
    
  xpos = xpos + xs
	
# Close training images
for i in range(len(trefs)):
	trefs[i] = None

# Print source raster metadata
print 'Driver: ',data_f.GetDriver().LongName
print 'Raster Sixe: ',data_f.RasterXSize,'x',data_f.RasterYSize
print 'Pixel Size: ',data_f.GetGeoTransform()[1],',',data_f.GetGeoTransform()[5]

#Create training class and model
tclass = sp.create_training_classes(tdata, tmask)
gmlc = sp.GaussianClassifier(tclass)
mldc = sp.MahalanobisDistanceClassifier(tclass)

# Read in data raster
data = np.zeros((data_f.RasterYSize, data_f.RasterXSize, data_nband))
for i in range(len(trefs)):
  for j in range(data_nband):
    data[:, :, j] = data_f.GetRasterBand(j+1).ReadAsArray()

#Classify image and display results
print("K-Means")
(kclmap,c) = sp.kmeans(data,kmeans_clusters,kmeans_iterations) #unsupervised
print("Gaussian")
gclmap = gmlc.classify_image(data) #supervised
print("Mahalanobis")
mclmap = mldc.classify_image(data) #supervised

#Define classification colors for array conversion
rlut = np.array([0, 255, 0,   255, 255, 255, 0,   0,   0, 100, 255, 255, 100])
glut = np.array([0, 255, 255, 0,   255, 0,   255, 0,   0, 255, 100, 255, 100])
blut = np.array([0, 255, 255, 255, 0,   0,   0,   255, 0, 255, 255, 100, 255])

#Convert kmeans array
print 'Kmeans Unsupervised Classification .tif Generation'
r = rlut[kclmap].astype('uint8')
g = glut[kclmap].astype('uint8')
b = blut[kclmap].astype('uint8')
		
rgb = np.dstack((r,g,b)).astype('uint8')
kclimg = Image.fromarray(rgb)
kclimg.save(out_path + 'kclimg.tif')

#Convert gaussian mean array
print("Gaussian Mean Supervised Image Classification TIFF Generation")
r = rlut[gclmap].astype('uint8')
g = glut[gclmap].astype('uint8')
b = blut[gclmap].astype('uint8')
		
rgb = np.dstack((r,g,b)).astype('uint8')
gclimg = Image.fromarray(rgb)
gclimg.save(out_path + 'gclimg.tif')

#Convert mahalanobis array
print("Gaussian Mean Supervised Image Classification TIFF Generation")
r = rlut[mclmap].astype('uint8')
g = glut[mclmap].astype('uint8')
b = blut[mclmap].astype('uint8')
		
rgb = np.dstack((r,g,b)).astype('uint8')
mclimg = Image.fromarray(rgb)
mclimg.save(out_path + 'mclimg.tif')
