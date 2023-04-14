# dune_mapping_orientation_OBIA
Python scripts that are part of a framework to map dunefields and quantify their orientation.

The Google Earth Engine (GEE) scripts and data used to map dunefields, i.e. classify ar region into dune vs non-dune areas, can be found here: https://code.earthengine.google.com/?accept_repo=users/mnowatzki/MScTHESIS_Nowatzki.


We provide a set of functions (*dunefield_OBIA_modules*) as well as scripts and data for the analysis of two dunefields in the Ili-Balkhash area (Zhalkum and Abdulkum). These can be customised and used to analyse other areas. The resulting classification rasters can be downloaded from GEE via the tasks tab.


Here, we are providing 4 scripts and a manual for **post-processing and calculating dunefield orientation** after dunefield mapping using eCognition (cf. Fitzsimmons et al., 2020) or GEE.




## How to use: 

**General:** The scripts are to be run via pyQGIS. ArcMap needed for the calculation of oriented minimum bounding boxes.


1) Run *script_clean_1_ecog.py* / *script_clean_1_GEE.py* depending on whether you are using an eCognition (vector) or GEE (raster) classification as input. In order to run the scripts, the path variables in the beginning of the script need to be filled in according to your local paths.

2) Check resulting .shp file and manually delete or separate unwanted large features (e.g. clusters of individual dunes).

3) Use ArcMap to calculate oriented minimum  bounding boxes around dune polygons

4) Run *script_clean_2_orient_ecog.py* / *script_clean_2_GEE.py* depending on whether your initial classification was conducted in eCognition (vector) or GEE (raster). In order to run the scripts, the path variables in the beginning of the script need to be changed according to your local paths.


## Your results are 


A) A .shp of dune polygons with orientations saved in the attribute table. You can colour them using the provided *style_orientation_maps.qml* file in QGIS.

B) An excel spreadsheet with the frequencies of the orientations in the dunefield. This can be used to create a dunerose showing the distribution of orientations / dominant orientations.











Fitzsimmons, K. E., Nowatzki, M., Dave, A. K., & Harder, H. (2020). Intersections between wind regimes, topography and sediment supply: Perspectives from aeolian landforms in Central Asia. Palaeogeography, Palaeoclimatology, Palaeoecology, 540, 109531.
