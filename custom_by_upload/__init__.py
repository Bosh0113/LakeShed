# coding=utf-8
import os
import time
import taudem_utils as tu
import get_dir_acc as gda
import common_utils as cu
import vector_rasterize as vr
import river_extract as re
import record_rivers as rr
import water_revise as wr
import slope_surface_extract as sse
import watershed_extract as we
import shutil
import gdal
import sys


# 方法主入口： 数据存储路径 DEM数据路径 湖泊/水库范围数据路径 河网提取阈值
def start_main(work_path, dem_tif, lakes_shp, river_th):
    start = time.perf_counter()

    # 过程数据存储路径
    process_path = work_path + '/process'
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # 结果数据存储路径
    result_path = work_path + '/result'
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    print("-------------------------------------DEM Pit Remove---------------------------------")
    stage_time = time.perf_counter()
    dem_filled_tif = process_path + "/dem_filled.tif"
    # DEM填洼
    tu.pit_remove(dem_tif, dem_filled_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("----------------------------Get Direction and Accumulation--------------------------")
    stage_time = time.perf_counter()
    dir_tif = process_path + "/dir.tif"
    acc_tif = process_path + "/acc.tif"
    # 计算流向、汇流累积量
    gda.get_dir_acc(process_path, dem_tif_path, dir_tif, acc_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("-----------------------------------Get Lakes Raster----------------------------------")
    stage_time = time.perf_counter()
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
    we.watershed_extract(process_path, dem_filled_tif, dir_tif, acc_tif, river_tif, water_s_s_tif_path)
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

    print("----------------------------------------Over----------------------------------------")
    end = time.perf_counter()
    print('Total time: ', end - start, 's')


def create_result_file(o_path):
    time.sleep(3)
    o_path = o_path + '\\c.txt'
    open(o_path, mode='w')


if __name__ == '__main__':
    ws_path = sys.argv[1]
    dem_tif_path = sys.argv[2]
    lakes_shp_path = sys.argv[3]
    river_threshold = float(sys.argv[4])
    if os.path.exists(dem_tif_path) and os.path.exists(lakes_shp_path):
        if river_threshold > 0:
            print('Running...')
            print('Parameter: ' + str(river_threshold))
            start_main(ws_path, dem_tif_path, lakes_shp_path, river_threshold)
            print('Over!')
        else:
            print('Bad Parameter!')
    else:
        print('No found!')
    time.sleep(2)
    print('Exit!')