# coding=utf-8
import os
import time
import get_data_from_RDD as gdfr
import filter_lakes as fl
import filter_lake_saga as fls
import common_utils as cu
import vector_rasterize as vr
import river_extract as re
import land_ocean as lo
import river_add_final as raf
import record_rivers as rr
import water_revise as wr
import slope_surface_extract as sse
import watershed_extract as we
import shutil
import gdal
import sys


# RDD数据目录路径
catalog_path = '/disk1/hydro_data/catalog'
# 湖泊/水库范围边界数据路径
o_lake_data = '/disk1/data/Hydro_Lake/full_lakes/lakes_gt_10km2_full.shp'


# 方法主入口： 数据存储路径 兴趣范围路径 湖泊/水库面积阈值 河网提取阈值
def start_main(work_path, geojson_path, lakes_area, river_th):
    start = time.perf_counter()

    # 基础数据存储路径
    data_path = work_path + '/data'
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # 过程数据存储路径
    process_path = work_path + '/process'
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # 结果数据存储路径
    result_path = work_path + '/result'
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    print("----------------------------------Search Basic Data----------------------------------")
    stage_time = time.perf_counter()
    # 从RDD中获取兴趣范围内的基本数据
    gdfr.get_basic_data(data_path, catalog_path, geojson_path)
    # 得到的基本数据所在路径
    dem_tif = data_path + '/dem.tif'
    acc_tif = data_path + '/acc.tif'
    dir_o_tif = data_path + '/dir_o.tif'
    dir_tif = data_path + '/dir.tif'
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("-----------------------------------Get Lakes Data----------------------------------")
    stage_time = time.perf_counter()
    # 兴趣范围转为shp格式
    extent_data = process_path + '/extent.shp'
    cu.geojson_to_shp(geojson_path, extent_data)
    # 提取兴趣范围内的湖泊/水库范围
    # lakes_shp = data_path + '/lakes_shp.shp'
    # fl.filter_lakes_extent_area(o_lake_data, extent_data, lakes_shp, lakes_area)
    lakes_shp = data_path + '/lakes_shp.shp'
    fls.clip_shp(geojson_path, o_lake_data, lakes_shp)
    # 将湖泊/水库栅格化同基本数据一致标准
    lakes_tif = process_path + '/lakes_99.tif'
    vr.lake_rasterize(lakes_shp, dir_tif, lakes_tif, -99, -9, 1)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("-------------------------------------Get Rivers-------------------------------------")
    stage_time = time.perf_counter()
    # 提取河网
    re.get_river(process_path, acc_tif, river_th)
    river_tif = process_path + "/stream.tif"
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("-------------------------------Add Finals to Rivers---------------------------------")
    stage_time = time.perf_counter()
    # 记录区域内的内流终点
    trace_starts = process_path + "/trace_starts.tif"
    final_record = process_path + '/finals.txt'
    seaside_record = process_path + "/seaside_record.txt"
    lo.get_trace_points(dir_tif, dir_o_tif, trace_starts, seaside_txt=seaside_record, final_txt=final_record)
    raf.add_final_to_river(dir_tif, final_record, river_tif, acc_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("------------------------------------Record Rivers------------------------------------")
    stage_time = time.perf_counter()
    # 记录河系信息
    rr.record_rivers(process_path, river_tif, acc_tif)
    river_record = process_path + "/river_record.txt"
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("----------------------------------Get Revised Water----------------------------------")
    stage_time = time.perf_counter()
    water_revised_path = process_path + "/lake.tif"
    cu.copy_tif_data(lakes_tif, water_revised_path)
    # 修正湖泊/水库边界
    wr.water_revise(water_revised_path, river_tif, river_record, dir_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("----------------------------------Get Slope Surface----------------------------------")
    stage_time = time.perf_counter()
    # 提取坡面和湖泊/水库
    sse.get_slope_surface(process_path, water_revised_path, dir_tif, acc_tif, river_th, -9)
    water_s_s_tif_path = process_path + "/water_slope.tif"
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("------------------------------------Get Watershed-----------------------------------")
    stage_time = time.perf_counter()
    # 提取子流域
    we.watershed_extract(process_path, dem_tif, dir_tif, acc_tif, river_tif, water_s_s_tif_path)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("-----------------------------------Copy Result Data----------------------------------")
    # 复制修正后的湖泊/水库、坡面流路、子流域以及河网矢量结果数据到文件夹
    print("-> Copy Water/Slope surface route/Stream...")
    stage_time = time.perf_counter()
    file_list = os.listdir(process_path)
    result_files = ["lake", "flow_path", "river_sub-basin"]
    for file in file_list:
        file_info = file.split(".")
        if file_info[0] in result_files:
            shutil.copy(process_path + "/" + file, result_path + "/" + file)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 复制河网栅格结果数据和重分类
    print("-> Copy/Reclassify Stream...")
    stage_time = time.perf_counter()
    river_e_tif = os.path.join(process_path, 'stream_erase.tif')
    river_ds = gdal.Open(river_e_tif)
    no_data_value = river_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(river_e_tif, result_path + "/river.tif", [[0]], [int(no_data_value)])
    river_ds = None
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 复制坡面结果数据和重分类
    print("-> Copy/Reclassify Slope surface...")
    stage_time = time.perf_counter()
    w_w_surface_ds = gdal.Open(water_s_s_tif_path)
    no_data_value = w_w_surface_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(water_s_s_tif_path, result_path + "/hillslope.tif",
                      [[-99]], [int(no_data_value)])
    w_w_surface_ds = None
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    shutil.rmtree(process_path)
    os.remove(dir_o_tif)

    print("----------------------------------------Over----------------------------------------")
    end = time.perf_counter()
    print('Total time: ', end - start, 's')


if __name__ == '__main__':
    ws_path = sys.argv[1]
    extent_geojson = sys.argv[2]
    river_threshold = float(sys.argv[3])
    lake_threshold = float(sys.argv[4])
    if os.path.exists(extent_geojson):
        if river_threshold > 0:
            print('Running...')
            print('Parameter: ' + str(river_threshold))
            start_main(ws_path, extent_geojson, river_threshold, lake_threshold)
            print('Over!')
        else:
            print('Bad Parameter!')
    else:
        print('No found!')
    time.sleep(2)
    print('Exit!')