# %%
import folium
import os
import numpy as np

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt 
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import MultiPolygon, Polygon
import rasterio as rio
from rasterio.plot import show
import rasterio.mask
import fiona

#import rioxarray module
import rioxarray
from rasterio.crs import CRS



# %%
user = 'username2' 
password = 'enterrealpassword!' 

api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

# %%
nReserve = gpd.read_file('shapefile/NewBritain-polygon.shp')
nReserve
# %%
m = folium.Map([-5.26755961052244, 150.00708990171134], zoom_start=11)

folium.GeoJson(nReserve).add_to(m)
m
# %%
footprint = None
for i in nReserve['geometry']:
    footprint = i
    
footprint

# %%
products = api.query(footprint,
                     date = ('20230301', '20230426'),
                     platformname = 'Sentinel-2',
                     processinglevel = 'Level-2A',
                     cloudcoverpercentage = (0,10))
# %%

len(products)
# %%
products_gdf = api.to_geodataframe(products)
products_gdf_sorted = products_gdf.sort_values(['cloudcoverpercentage'], ascending=[True])
products_gdf_sorted
# %%
api.download("9ee21c4d-69bc-49cd-9da1-722ec8cd12c6")

 # %%
!unzip S2B_MSIL2A_20230319T002709_N0509_R016_T55MHQ_20230319T015951.zip --quite
# %%
# Open Bands 4, 3 and 2 with Rasterio
R10 = 'S2B_MSIL2A_20230319T002709_N0509_R016_T55MHQ_20230319T015951.SAFE/GRANULE/L2A_T55MHQ_A031502_20230319T002711/IMG_DATA/R10m'

b4 = rio.open(R10+'/T55MHQ_20230319T002709_B04_10m.jp2')
b3 = rio.open(R10+'/T55MHQ_20230319T002709_B03_10m.jp2')
b2 = rio.open(R10+'/T55MHQ_20230319T002709_B02_10m.jp2')
# %%
b4.count, b4.width, b4.height
# %%
fig, ax = plt.subplots(1, figsize=(20, 20))
show(b4, ax=ax)
plt.show()
# %%
with rio.open('RGB.tiff','w',driver='Gtiff', width=b4.width, height=b4.height, 
              count=3,crs=b4.crs,transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
    rgb.write(b2.read(1),1) 
    rgb.write(b3.read(1),2) 
    rgb.write(b4.read(1),3) 
    rgb.close()
# %%

# Open the raster file and print its CRS
with rasterio.open('RGB.tiff') as src:
    print(src.crs)
# %%

#src = rio.open(r"RGB.tiff")
nReserve_proj = nReserve.to_crs({'init': 'epsg:32755'})

with rio.open("RGB.tiff") as src:
    out_image, out_transform = rio.mask.mask(src, nReserve_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    
with rasterio.open("RGB_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)
# %%
msk = rio.open(r"RGB_masked.tif")
fig, ax = plt.subplots(1, figsize=(18, 18))
show(msk.read([1,2,3]))
plt.show
# %%
b4 = rio.open(R10+'/T55MHQ_20230319T002709_B04_10m.jp2')
b8 = rio.open(R10+'/T55MHQ_20230319T002709_B08_10m.jp2')

# %%
red = b4.read()
nir = b8.read()
# %%
ndvi = (nir.astype(float)-red.astype(float))/(nir+red)
# %%
meta = b4.meta

meta.update(driver='GTiff')
meta.update(dtype=rasterio.float32)

with rasterio.open('NDVI.tif', 'w', **meta) as dst:
    dst.write(ndvi.astype(rasterio.float32))
# %%
msk = rio.open(r"NDVI.tif")
fig, ax = plt.subplots(1, figsize=(18, 18))
show(msk.read())
plt.show
# %%
raster_file = rioxarray.open_rasterio("RGB.tiff", masked=True).squeeze()



# %%
#test4
# %%
