#!/usr/bin/python
from osgeo import gdal
from gdalconst import *
import numpy as np
import spectral as sp
from PIL import Image
import sys

input = sys.argv

#User defined variables
path_to_source_raster = input[1]
src_raster_num_bands = int(input[4])
classification_images_num_bands = int(input[5])
path_to_classification_images = input[2]
list_classification_images = np.array(input[3].split(','))

path_to_output = path_to_source_raster[:-7]

####Make class mask array####
####THIS MUST BE ADDED TO WHEN YOU ADD A CLASSIFICATION IMAGE####
####ADD IMAGES TO THE END OF THE STRING LIST AND THE BOTTOM OF THIS LIST####
####SEE "class.txt" FILE FOR CLASS INDICES###
zer = np.zeros((10,10))
#citymsk = zer
#city2msk = zer
#cloudmsk = zer + 1
#cloud2msk = np.zeros((200,10)) + 1
#ruralmsk = zer + 2
#rural2msk = np.zeros((50,10)) + 2
#shadowmsk = zer + 3
#watermsk = zer + 4
azer = np.zeros((335,10))
agrimsk = azer + 1
czer = np.zeros((248,10))
citymsk = czer + 2
#undevmsk = zer + 2
wzer = np.zeros((175,10))
watermsk = wzer + 3
uzer = np.zeros((340,10))
undevmsk = uzer + 4
###ADD NEW CLASS MASK ARRAYS BELOW HERE###


#Generate classification image strings for later use
mskstr = ''
allstr = ''
for i in list_classification_images:
	mskstr = mskstr + i + 'msk,'
	allstr = allstr + i + 'all,'

mskstr = mskstr[:-1]
allstr = allstr[:-1]

#open the source raster
src_raster = gdal.Open(path_to_source_raster, GA_ReadOnly)

#open the classification images
for i in list_classification_images:
	cmd1 = i + " = gdal.Open('" + path_to_classification_images + i + ".tif')"
	exec cmd1

#print some relevant things for fun
print 'Driver: ',src_raster.GetDriver().LongName
print 'Raster Sixe: ',src_raster.RasterXSize,'x',src_raster.RasterYSize
print 'Origin: ',src_raster.GetGeoTransform()[0],',',src_raster.GetGeoTransform()[3]
print 'Pixel Size: ',src_raster.GetGeoTransform()[1],',',src_raster.GetGeoTransform()[5]
print 'Metadata: ',src_raster.GetMetadata()

#Copy the source raster to a 3D numpy array and save its size
cmd1 = ''
cmd2 = 'barall = np.dstack(('

for i in range(src_raster_num_bands):
	j = str(i + 1)
	cmd1 = cmd1 + 'bar' + j + ' = np.array(src_raster.GetRasterBand(' + j + ').ReadAsArray())\n'
	cmd2 = cmd2 + 'bar' + j + ','
	
exec cmd1
cmd2 = cmd2 + '))'
exec cmd2

(m,n,x) = barall.shape

#Copy the classification images into 3D numpy arrays
for i in list_classification_images:
	cmd1 = ''
	cmd2 = i + 'all = np.dstack(('
	for q in range(classification_images_num_bands):
		j = str(q + 1)
		cmd1 = cmd1 + i + 'ar' + j + ' = np.array(' + i + '.GetRasterBand(' + j + ').ReadAsArray())\n'
		cmd2 = cmd2 + i + 'ar' + j + ','
	exec cmd1
	cmd2 = cmd2 + '))'
	exec cmd2

#Concatenate the classification image arrays and mask arrays
cm1 = 'maskar = np.concatenate((' + mskstr + '))'
cm2 = 'classar = np.concatenate((' + allstr + '))'
exec cm1
exec cm2

#Adjust (either zero-pad or cut) classification array to work with source raster
(cx,cy) = maskar.shape
if src_raster_num_bands > classification_images_num_bands:
	zerar = np.zeros((cx,cy))
	diff = src_raster_num_bands - classification_images_num_bands
	for i in range(diff):
		classar = np.dstack((classar,zerar))

#Create training class and model
trcls = sp.create_training_classes(classar,maskar)
gmlc = sp.GaussianClassifier(trcls)
mldc = sp.MahalanobisDistanceClassifier(trcls)

#Classify image and display results
(kclmap,c) = sp.kmeans(barall,12,30) #unsupervised
gclmap = gmlc.classify_image(barall) #supervised
mclmap = mldc.classify_image(barall) #supervised

#Define classification colors for array conversion
def num2colR(arg):
	switcher = {
		1: 255,
		2: 0,
		3: 255,
		4: 255,
		5: 255,
		6: 0,
		7: 0,
		8: 0,
		9: 100,
		10: 255,
		11: 255,
		12: 100,
	}
	return switcher.get(arg,0)
	
def num2colG(arg):
	switcher = {
		1: 255,
		2: 255,
		3: 0,
		4: 255,
		5: 0,
		6: 255,
		7: 0,
		8: 0,
		9: 255,
		10: 100,
		11: 255,
		12: 100,
	}
	return switcher.get(arg,0)
	
def num2colB(arg):
	switcher = {
		1: 255,
		2: 255,
		3: 255,
		4: 0,
		5: 0,
		6: 0,
		7: 255,
		8: 0,
		9: 255,
		10: 255,
		11: 100,
		12: 255,
	}
	return switcher.get(arg,0)
	

#Convert kmeans array
r = np.array(kclmap).astype('uint8')
g = np.array(kclmap).astype('uint8')
b = np.array(kclmap).astype('uint8')

print 'Kmeans Unsupervised Classification .tif Generation'
#pc = 0
#for i in range(m):
#	pcc = int(float(i)/m*100)
#	if pcc != pc:
#		pc = pcc
#		sys.stdout.write("  " + str(pc) +'%\r')
#		sys.stdout.flush()
		
#	for j in range(n):
#		r[i][j] = num2colR(r[i][j])
#		g[i][j] = num2colG(g[i][j])
#		b[i][j] = num2colB(b[i][j])
		
#rgbcom = np.dstack((r,g,b)).astype('uint8')
#kclimg = Image.fromarray(rgbcom)
#kclimg.save(path_to_output + 'kclimg.tif')
	

#Convert gaussian mean array
r = np.array(gclmap).astype('uint8')
g = np.array(gclmap).astype('uint8')
b = np.array(gclmap).astype('uint8')

print '  100%'

print 'Gaussian Mean Supervised Image Classification .tif Generation'
pc = 0
for i in range(m):
	pcc = int(float(i)/m*100)
	if pcc != pc:
		pc = pcc
		sys.stdout.write("  " + str(pc) +'%\r')
		sys.stdout.flush()
		
	for j in range(n):
		r[i][j] = num2colR(r[i][j])
		g[i][j] = num2colG(g[i][j])
		b[i][j] = num2colB(b[i][j])
		
rgbcom = np.dstack((r,g,b)).astype('uint8')
gclimg = Image.fromarray(rgbcom)
gclimg.save(path_to_output + 'gclimg.tif')

print '  100%'


#Convert mahalanobis array
r = np.array(mclmap).astype('uint8')
g = np.array(mclmap).astype('uint8')
b = np.array(mclmap).astype('uint8')

print 'Mahalanobis Supervised Classification .tif Generation'
pc = 0
for i in range(m):
	pcc = int(float(i)/m*100)
	if pcc != pc:
		pc = pcc
		sys.stdout.write("  " + str(pc) +'%\r')
		sys.stdout.flush()
				
	for j in range(n):
		r[i][j] = num2colR(r[i][j])
		g[i][j] = num2colG(g[i][j])
		b[i][j] = num2colB(b[i][j])
		
rgbcom = np.dstack((r,g,b)).astype('uint8')
mclimg = Image.fromarray(rgbcom)
mclimg.save(path_to_output + 'mclimg.tif')

print '  100%'





