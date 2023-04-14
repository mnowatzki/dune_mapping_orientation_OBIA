## Maike Nowatzki, 26.08.2019 Clean-Out Script
# for raster classification results from GEE

## imports

from qgis.core import *
from qgis.utils import *
from qgis import processing
import jenkspy #for jenks natural breaks
import math #for pi


# paths
path_classification_results_raster = 'path/to/file' # .tif file of dune vs non dune classiication
path_classification_results_vec = 'path/to/file'
path_only_dunes = 'path/to/file'
path_studyarea = 'path/to/file' #.shp file (polygon) of study area
path_only_dunes_within = 'path/to/file'
path_only_dunes_within_large = 'path/to/file'




##load raster layer classification into QGIS
  
area_layer_raster = iface.addRasterLayer(
        path_classification_results_raster, 
        "area_layer_raster")
if not area_layer_raster: 
    print ("Layer failed to load")
    
    
## vectorizing raster image and load

area_layer = processing.run("gdal:polygonize", {
        'INPUT':area_layer_raster,
        'BAND':1,
        'FIELD':'DN',
        'EIGHT_CONNECTEDNESS':False,
        'EXTRA':'',
        'OUTPUT':path_classification_results_vec})
        
area_layer_onlydunes = iface.addVectorLayer(
        path_classification_results_vec, 
        "area_layer", 
        "ogr")
if not area_layer: 
    print ("Layer failed to load")


##filtering for dune features & creating new layer of them
area_layer = iface.activeLayer()
area_layer.selectByExpression('"DN"=\'1\'', QgsVectorLayer.SetSelection)

area_layer_onlydunes = processing.run("native:saveselectedfeatures", {
        'INPUT': area_layer, 
        'OUTPUT': path_only_dunes})

area_layer_onlydunes = iface.addVectorLayer(
        path_only_dunes, 
        "area_layer_onlydunes", 
        "ogr")
if not area_layer_onlydunes: 
    print ("Layer failed to load")

area_layer.removeSelection()



##remove classification of black noData area outside of dune field

#load vector layer shape (dune field) into QGIS
  
area_layer_shape = iface.addVectorLayer(
        path_studyarea, 
        "area_layer_shape", 
        "ogr")
if not area_layer_shape: 
    print ("Layer failed to load")


# mark features that are completely within vector layer shape

processing.run("qgis:selectbylocation", {
        'INPUT': area_layer_onlydunes, 
        'INTERSECT': area_layer_shape, 
        'PREDICATE': 6, 
        'METHOD': 0})

# create new layer out of only features that are completely within vector layer shape of dune field

area_layer_onlydunes_within = processing.run("native:saveselectedfeatures", {
        'INPUT': area_layer_onlydunes, 
        'OUTPUT': path_only_dunes_within})

area_layer_onlydunes_within = iface.addVectorLayer(
        path_only_dunes_within, 
        "area_layer_onlydunes_within", 
        "ogr")
if not area_layer_onlydunes_within: 
    print ("Layer failed to load")

area_layer_onlydunes.removeSelection()


## calculate area of each feature

# create new column in attribute table "Area"
 
lProvider = area_layer_onlydunes_within.dataProvider()
lProvider.addAttributes( [QgsField("Area",QVariant.Double) ] )


# calculate area for each polygon and fill in attribute column "Area"

with edit(area_layer_onlydunes_within):
    
    for feature in area_layer_onlydunes_within.getFeatures():
 
        area = feature.geometry().area()
        area_layer_onlydunes_within.changeAttributeValue(feature.id(), 1, area)
        
area_layer_onlydunes_within.updateFeature(feature)



## calculate Jenks Breaks for column "Area" and create layer of all but the lowest Jenks class

# Get attributes of column "Area" (store column as list)

area_list = [feature.attributes()[1] for feature in area_layer_onlydunes_within.getFeatures()]
  

# calculate Jenks Natural Breaks and assign second value as variable

jenks_breaks = jenkspy.jenks_breaks(area_list, nb_class=10)
jenks_var_sep_minclass = (jenks_breaks[1])
print(jenks_var_sep_minclass)


# filtering for dune features that are large enough & creating new layer of them

area_layer_onlydunes_within = iface.activeLayer()
area_layer_onlydunes_within.selectByExpression('"Area" > {}'.format(jenks_var_sep_minclass), QgsVectorLayer.SetSelection)

area_layer_onlydunes_within_large = processing.run("native:saveselectedfeatures", {
        'INPUT': area_layer_onlydunes_within, 
        'OUTPUT': path_only_dunes_within_large})

area_layer_onlydunes_within_large = iface.addVectorLayer(
        path_only_dunes_within_large, 
        "area_layer_onlydunes_within_large", 
        "ogr")

if not area_layer_onlydunes_within_large: 
    print ("Layer failed to load")

  
area_layer_onlydunes_within.removeSelection()









    










