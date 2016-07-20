from osgeo import gdal
from gdalconst import *
import numpy as np
import spectral as sp
from PIL import Image

#User defined variables
path_to_source_raster = '/Users/Michael/Desktop/84land/out.tif'
pcls = '/Users/Michael/Desktop/84land/'
lci = np.array(['cloud','shadow','water','rural','city','cloud2','rural2','city2'])

#Generate classification image strings for later use
mskstr = ''
allstr = ''
for i in lci:
	mskstr = mskstr + i + 'msk,'
	allstr = allstr + i + 'all,'

mskstr = mskstr[:-1]
allstr = allstr[:-1]

#open the source raster
src_raster = gdal.Open(path_to_source_raster, GA_ReadOnly)

#open the classification images
for i in lci:
	cmd1 = i + " = gdal.Open('" + pcls + i + ".tif')"
	exec cmd1

#print some relevant things for fun
print 'Driver: ',src_raster.GetDriver().LongName
print 'Raster Sixe: ',src_raster.RasterXSize,'x',src_raster.RasterYSize
print 'Origin: ',src_raster.GetGeoTransform()[0],',',src_raster.GetGeoTransform()[3]
print 'Pixel Size: ',src_raster.GetGeoTransform()[1],',',src_raster.GetGeoTransform()[5]
print 'Metadata: ',src_raster.GetMetadata()

#Copy the source raster to a numpy array and save its size
bar1 = np.array(src_raster.GetRasterBand(1).ReadAsArray())
bar2 = np.array(src_raster.GetRasterBand(2).ReadAsArray())
bar3 = np.array(src_raster.GetRasterBand(3).ReadAsArray())
bar4 = np.array(src_raster.GetRasterBand(4).ReadAsArray())
(m,n) = bar1.shape

#stack 2d arrays into one 3d
barall = np.dstack((bar1,bar2,bar3,bar4))

#Copy the classification images into 3D numpy arrays
for i in lci:
	cmd1 = i + 'ar1 = np.array(' + i + '.GetRasterBand(1).ReadAsArray())'
	cmd2 = i + 'ar2 = np.array(' + i + '.GetRasterBand(2).ReadAsArray())'
	cmd3 = i + 'ar3 = np.array(' + i + '.GetRasterBand(3).ReadAsArray())'
	cmd4 = i + 'ar4 = np.array(' + i + '.GetRasterBand(4).ReadAsArray())'
	cmd5 = i + 'all = np.dstack((' + i + 'ar1,' + i + 'ar2,' + i + 'ar3,' + i + 'ar4))'
	exec cmd1 
	exec cmd2 
	exec cmd3 
	exec cmd4 
	exec cmd5

#Concatenate the classification arrays
cm1 = 'classar = np.concatenate((' + allstr + '))'
exec cm1

#Make class mask array
zer = np.zeros((10,10))
cloudmsk = zer + 1
shadowmsk = zer + 2
watermsk = zer + 3
ruralmsk = zer + 4
citymsk = zer + 5
cloud2msk = np.zeros((200,10)) + 1
rural2msk = np.zeros((50,10)) + 4
city2msk = zer + 5
cm1 = 'maskar = np.concatenate((' + mskstr + '))'
exec cm1

#Create training class and model
trcls = sp.create_training_classes(classar,maskar)
gmlc = sp.GaussianClassifier(trcls)
mldc = sp.MahalanobisDistanceClassifier(trcls)

#Classify image and display results
(kclmap,c) = sp.kmeans(barall,12,20) #unsupervised
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
pc = 0
for i in range(m):
	pcc = int(float(i)/m*100)
	if pcc != pc:
		pc = pcc
		print str(pc) +'%'
		
	for j in range(n):
		r[i][j] = num2colR(r[i][j])
		g[i][j] = num2colG(g[i][j])
		b[i][j] = num2colB(b[i][j])
		
rgbcom = np.dstack((r,g,b)).astype('uint8')
kclimg = Image.fromarray(rgbcom)
kclimg.save('kclimg.tif')
	

#Convert gaussian mean array
r = np.array(gclmap).astype('uint8')
g = np.array(gclmap).astype('uint8')
b = np.array(gclmap).astype('uint8')

print 'Gaussian Mean Supervised Image Classification .tif Generation'
pc = 0
for i in range(m):
	pcc = int(float(i)/m*100)
	if pcc != pc:
		pc = pcc
		print str(pc) + '%'
		
	for j in range(n):
		r[i][j] = num2colR(r[i][j])
		g[i][j] = num2colG(g[i][j])
		b[i][j] = num2colB(b[i][j])
		
rgbcom = np.dstack((r,g,b)).astype('uint8')
gclimg = Image.fromarray(rgbcom)
gclimg.save('gclimg.tif')


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
		print str(pc) + '%'
		
	for j in range(n):
		r[i][j] = num2colR(r[i][j])
		g[i][j] = num2colG(g[i][j])
		b[i][j] = num2colB(b[i][j])
		
rgbcom = np.dstack((r,g,b)).astype('uint8')
mclimg = Image.fromarray(rgbcom)
mclimg.save('mclimg.tif')

#Palette experimentation
#pal.putpalette([
#    255,255,255, 
#      0,255,255, 
#    255,  0,255, 
#    255,255,  0,
#    255,  0,  0,
#      0,255,  0,
#    
#])

#sp.imshow(classes=j) #show unsupervised
#sp.imshow(classes=gclmap) #show gaussian supervised
#sp.imshow(classes=mclmap) #show other supervised



