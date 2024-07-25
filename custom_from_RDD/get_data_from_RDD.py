# coding=utf-8
import clip_tif_gdal as ct
import data_search as ds
import dir_reclassify as dr
import os
import time
import shutil


# 示例：工作空间路径 RDD存储路径 GeoJson范围数据路径
def get_basic_data(storage_path, catalog_path, geojson_path):

    start = time.perf_counter()

    # 工作空间路径
    temp_path = storage_path + "/temp"
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # 查询计算区域的数据
    print("----------------------------------Search Raster Data----------------------------------")
    stage_time = time.perf_counter()
    # DEM数据路径
    dem_tif_path = temp_path + "/dem.tif"
    # 流向数据路径
    dir_tif_path = temp_path + "/dir.tif"
    # 汇流累积量数据路径
    acc_tif_path = temp_path + "/acc.tif"
    print("Output Data.")
    ds.data_search(catalog_path, geojson_path, dem_tif_path, dir_tif_path, acc_tif_path)

    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')


    # 裁剪研究区域的数据
    print("----------------------------------Crop Raster Data----------------------------------")
    stage_time = time.perf_counter()
    dem_clip = storage_path + "/dem.tif"
    dir_clip = storage_path + "/dir_o.tif"
    acc_clip = storage_path + "/acc.tif"
    ct.geojson_clip_tif(geojson_path, dem_tif_path, dem_clip)
    ct.geojson_clip_tif(geojson_path, dir_tif_path, dir_clip)
    ct.geojson_clip_tif(geojson_path, acc_tif_path, acc_clip)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 流向数据重分类
    print("----------------------------------Reclassify Direction Data----------------------------------")
    dir_reclass = storage_path + '/dir.tif'
    dr.reclassify_dir(dir_clip, dir_reclass)

    shutil.rmtree(temp_path)