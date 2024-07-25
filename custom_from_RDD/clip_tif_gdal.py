# coding=utf-8
import os
import geopandas

# geojson转shapefile: geojson路径 shapefile路径
def geojson_to_shp(geoj_path, shp_path):
    geoj = geopandas.read_file(geoj_path)
    geoj.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")


# shapefile裁切tif: shapefile路径 tif路径 结果路径
def shp_clip_tif(shp_path, raster_path, result_path):
    print("Crop Raster by Shp...")
    cmd = 'gdalwarp -cutline '+shp_path+' -crop_to_cutline '+raster_path+' ' +result_path
    print(cmd)
    d = os.system(cmd)
    print(d)

def geojson_clip_tif(geoj_path, raster_path, result_path):
    shp_path = geoj_path[:-7]+'shp'
    geojson_to_shp(geoj_path, shp_path)
    shp_clip_tif(shp_path, raster_path, result_path)