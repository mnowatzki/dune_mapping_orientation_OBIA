## Maike Nowatzki, 22.12.2019 Clean-Out Script Nr 2
# for raster classification results from GEE
# to be run after script_clean_1_GEE

## set prerequisites

from qgis.core import *
from qgis.utils import *
from qgis import processing
import jenkspy #for jenks natural breaks
import math #for pi
from pandas import DataFrame #for excel spreadsheet


# paths
path_ombb = 'path/to/file' #.shp bounding box file created in Arc
path_only_dunes_within_large = 'path/to/file' # .tif file resulting from script_clean_1
path_only_dunes_within_large_ib = 'path/to/file'
path_join1 = 'path/to/file'
path_join2 = 'path/to/file'
path_join2_isoperi = 'path/to/file'
path_excel = 'path/to/file'


    
##load OMBB layer (created by ArcGIS)
  
area_layer_onlydunes_within_large_OMBB = iface.addVectorLayer(
        path_ombb, 
        "area_layer_onlydunes_within_large_OMBB", 
        "ogr")
    
if not area_layer_onlydunes_within_large_OMBB: 
    print ("Layer failed to load")



## calculate area, perimeter, and isoperimetric quotient for boxes

# create new column in attribute table "areabx"
 
lProvider = area_layer_onlydunes_within_large_OMBB.dataProvider()
lProvider.addAttributes( [QgsField("areabx",QVariant.Double) ] )


# calculate area for each polygon and fill in attribute column "areabx"

with edit(area_layer_onlydunes_within_large_OMBB):
    
    for feature in area_layer_onlydunes_within_large_OMBB.getFeatures():

        areabox = feature.geometry().area()
        area_layer_onlydunes_within_large_OMBB.changeAttributeValue(feature.id(), 4, areabox)

area_layer_onlydunes_within_large_OMBB.updateFeature(feature)

iface.vectorLayerTools().stopEditing(area_layer_onlydunes_within_large_OMBB)


# create new column for perimeter 

lProvider = area_layer_onlydunes_within_large_OMBB.dataProvider()
lProvider.addAttributes( [QgsField("peribx",QVariant.Double) ] )



# calculate perimeter for column peribx

with edit(area_layer_onlydunes_within_large_OMBB):
    
    for feature in area_layer_onlydunes_within_large_OMBB.getFeatures():
        peribox = feature.geometry().length()
        area_layer_onlydunes_within_large_OMBB.changeAttributeValue(feature.id(), 5, peribox)

area_layer_onlydunes_within_large_OMBB.updateFeature(feature)

iface.vectorLayerTools().stopEditing(area_layer_onlydunes_within_large_OMBB)


# create new column for isoperimetric quotient

lProvider = area_layer_onlydunes_within_large_OMBB.dataProvider()
lProvider.addAttributes( [QgsField("isobx",QVariant.Double) ] )
fieldlist = ['areabx','peribx']
field_indexes = [area_layer_onlydunes_within_large_OMBB.dataProvider().fieldNameIndex(f) for f in fieldlist]


# calculate isoperimetric quotient for column "isobx"

with edit(area_layer_onlydunes_within_large_OMBB):
    
    for feature in area_layer_onlydunes_within_large_OMBB.getFeatures():
 
        isobox = (4.0 * math.pi * feature.attributes()[field_indexes[0]])/(feature.attributes()[field_indexes[1]] **2)
        area_layer_onlydunes_within_large_OMBB.changeAttributeValue(feature.id(), 6, isobox)

area_layer_onlydunes_within_large_OMBB.updateFeature(feature)

iface.vectorLayerTools().stopEditing(area_layer_onlydunes_within_large_OMBB)



## load dune polygon layer created in script_cleanout_1

area_layer_onlydunes_within_large = iface.addVectorLayer(
        path_only_dunes_within_large, 
        "area_layer_onlydunes_within_large", 
        "ogr")
    
if not area_layer_onlydunes_within_large: 
    print ("Layer failed to load")



## join OMBB to dune polygons using inner buffer of polygons

# calculate inner buffer of dune polygons with -1 distance and load it

processing.run("native:buffer", {
        'INPUT':path_only_dunes_within_large,
        'DISTANCE':-1,
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':False,
        'OUTPUT':path_only_dunes_within_large_ib})

area_layer_onlydunes_within_large_ib = iface.addVectorLayer(
        path_only_dunes_within_large_ib, 
        "area_layer_onlydunes_within_large_ib", 
        "ogr")
if not area_layer_onlydunes_within_large_ib: 
    print ("Layer failed to load")

# join OMBB to inner buffer of polygons and add layer

processing.run("qgis:joinattributesbylocation", {
        'INPUT': path_only_dunes_within_large_ib,
        'JOIN': path_ombb,
        'PREDICATE': "5",
        'JOIN_FIELDS':[],
        'METHOD':0,
        'DISCARD_NONMATCHING': True,
        'PREFIX':"",
        'OUTPUT': path_join1}) 


area_layer_onlydunes_within_large_joinibOMBB = iface.addVectorLayer(
        path_join1, 
        "area_layer_onlydunes_within_large_joinibOMBB", 
        "ogr")
if not area_layer_onlydunes_within_large_joinibOMBB: 
    print ("Layer failed to load")
    

# delete unnecessary columns DN (will be double after next join otherwise)

area_layer_onlydunes_within_large_joinibOMBB = iface.activeLayer()
res = area_layer_onlydunes_within_large_joinibOMBB.dataProvider().deleteAttributes([0,3])
area_layer_onlydunes_within_large_joinibOMBB.updateFields()

area_layer_onlydunes_within_large_joinibOMBB.updateFeature(feature)



# join inner buffer polygons to normal dune polygons, add layer

processing.run("qgis:joinattributesbylocation", {
        'INPUT': path_only_dunes_within_large,
        'JOIN': path_join1,
        'PREDICATE': "1",
        'JOIN_FIELDS':[],
        'METHOD':0,
        'DISCARD_NONMATCHING': True,
        'PREFIX':"",
        'OUTPUT': path_join2}) 

area_layer_onlydunes_within_large_finaljoin = iface.addVectorLayer(
        path_join2, 
        "area_layer_onlydunes_within_large_finaljoin", 
        "ogr")
if not area_layer_onlydunes_within_large_finaljoin: 
    print ("Layer failed to load")


# count numbers of OMBB, dune polygons, and joined features to make sure it's the same number


ct_ombb = area_layer_onlydunes_within_large_OMBB.featureCount()
print("Nr. of OMBB features:", ct_ombb)

ct_dunepoly = area_layer_onlydunes_within_large.featureCount()
print("Nr. of dune polygon features:", ct_dunepoly)

ct_finaljoin = area_layer_onlydunes_within_large_finaljoin.featureCount()
print ("Nr of final joined features:", ct_finaljoin)

if ct_ombb == ct_dunepoly == ct_finaljoin:
    print("*************** Equal feature numbers - OK ***************")
    
else:
    print("*************** Feature numbers are not equal - need to be checked! ***************")




## filter finaljoin polygons for small enough isoperi of OMBB (isobx)


area_layer_onlydunes_within_large_finaljoin = iface.activeLayer()
area_layer_onlydunes_within_large_finaljoin.selectByExpression('"isobx" >= 0.7', QgsVectorLayer.AddToSelection)

area_layer_onlydunes_within_large_finaljoin.invertSelection()


area_layer_onlydunes_within_large_finaljoin_isoperi = processing.run("native:saveselectedfeatures", {
        'INPUT': area_layer_onlydunes_within_large_finaljoin, 
        'OUTPUT': path_join2_isoperi})

area_layer_onlydunes_within_large_finaljoin_isoperi = iface.addVectorLayer(
        path_join2_isoperi, 
        "area_layer_onlydunes_within_large_finaljoin_isoperi", 
        "ogr")
if not area_layer_onlydunes_within_large_finaljoin_isoperi: 
    print ("Layer failed to load")

area_layer_onlydunes_within_large_finaljoin.removeSelection()


# delete unnecessary columns

area_layer_onlydunes_within_large_finaljoin_isoperi = iface.activeLayer()
res = area_layer_onlydunes_within_large_finaljoin_isoperi.dataProvider().deleteAttributes([0,2,3]) 

area_layer_onlydunes_within_large_finaljoin_isoperi.updateFeature(feature)



## calculate angle in a 0-180 degree way (North to South, right half of compass; north is 0, south is 180)

# create new column for angle (angle_true)

lProvider = area_layer_onlydunes_within_large_finaljoin_isoperi.dataProvider()
lProvider.addAttributes( [QgsField("angle_true",QVariant.Double) ] )
fieldlist = ['angle_arc']
field_indexes = [area_layer_onlydunes_within_large_finaljoin_isoperi.dataProvider().fieldNameIndex(f) for f in fieldlist]


# calculate 0-180 angle for column angle_true

with edit(area_layer_onlydunes_within_large_finaljoin_isoperi):
    
    for feature in area_layer_onlydunes_within_large_finaljoin_isoperi.getFeatures():
 
        angletrue = 90.0 + feature.attributes()[field_indexes[0]]
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 6, angletrue)
        
area_layer_onlydunes_within_large_finaljoin_isoperi.updateFeature(feature)

iface.vectorLayerTools().stopEditing(area_layer_onlydunes_within_large_finaljoin_isoperi)


## calculate orientation strings

# add column for orientation string 

lProvider = area_layer_onlydunes_within_large_finaljoin_isoperi.dataProvider()
lProvider.addAttributes( [QgsField("angle_txt",QVariant.String) ] )
fieldlist = ['angle_true']
field_indexes = [area_layer_onlydunes_within_large_finaljoin_isoperi.dataProvider().fieldNameIndex(f) for f in fieldlist]

area_layer_onlydunes_within_large_finaljoin_isoperi.startEditing()
for feature in area_layer_onlydunes_within_large_finaljoin_isoperi.getFeatures():
    if (feature['angle_true'] >= 0 and feature['angle_true'] <= 11.25) or (feature['angle_true'] > 168.75 and feature['angle_true']<= 180):
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'N-S')
    elif feature['angle_true'] > 11.25 and feature['angle_true'] <= 33.75:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'NNE-SSW')
    elif feature['angle_true'] > 33.75 and feature['angle_true'] <= 56.25:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'NE-SW')
    elif feature['angle_true'] > 56.25 and feature['angle_true'] <=78.75:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'ENE-WSW')
    elif feature['angle_true'] > 78.75 and feature['angle_true'] <= 101.25:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'E-W')
    elif feature['angle_true'] > 101.25 and feature['angle_true'] <= 123.75:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'ESE-WNW')
    elif feature['angle_true'] > 123.75 and feature['angle_true'] <= 146.25:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'SE-NW')
    elif feature['angle_true'] > 146.25 and feature['angle_true'] <= 168.75:
        area_layer_onlydunes_within_large_finaljoin_isoperi.changeAttributeValue(feature.id(), 7, 'SSE-NNW')
        
        
area_layer_onlydunes_within_large_finaljoin_isoperi.commitChanges()

iface.vectorLayerTools().stopEditing(area_layer_onlydunes_within_large_finaljoin_isoperi)



# select each orientation and print out + save in excel file

area_layer_onlydunes_within_large_finaljoin_isoperi = iface.activeLayer()


area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'N-S\'', QgsVectorLayer.SetSelection)
ct_n = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of N-S features:", ct_n)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'NNE-SSW\'', QgsVectorLayer.SetSelection)
ct_nne = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of NNE-SSW features:", ct_nne)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'NE-SW\'', QgsVectorLayer.SetSelection)
ct_ne = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of NE-SW features:", ct_ne)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'ENE-WSW\'', QgsVectorLayer.SetSelection)
ct_ene = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of ENE-WSW features:", ct_ene)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'E-W\'', QgsVectorLayer.SetSelection)
ct_e = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of E-W features:", ct_e)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'ESE-WNW\'', QgsVectorLayer.SetSelection)
ct_ese = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of ESE-WNW features:", ct_ese)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'SE-NW\'', QgsVectorLayer.SetSelection)
ct_se = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of SE-NW features:", ct_se)

area_layer_onlydunes_within_large_finaljoin_isoperi.selectByExpression('"angle_txt" =\'SSE-NNW\'', QgsVectorLayer.SetSelection)
ct_sse = area_layer_onlydunes_within_large_finaljoin_isoperi.selectedFeatureCount()
print("Nr. of SSE-NNW features:", ct_sse)


l1 = [ct_n]
l2 = [ct_nne]
l3 = [ct_ne]
l4 = [ct_ene]
l5 = [ct_e]
l6 = [ct_ese]
l7 = [ct_se]
l8 = [ct_sse]

df = DataFrame({'N-S': l1, 'NNE-SSW': l2, 'NE-SW': l3, 'ENE-WSW': l4, 'E-W': l5, 'ESE-WNW': l6, 'SE-NW': l7, 'SSE-NNW': l8})
df
df.to_excel(path_excel, sheet_name='area', index=False)








