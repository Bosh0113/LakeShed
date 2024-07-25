# coding=utf-8
import os
import time
import gdal
import taudem_utils as tu
import common_utils as cu


# 获取NoData标识
def get_nodata_value(data_ds):
    nodata = data_ds.GetRasterBand(1).GetNoDataValue()
    if nodata is None:
        nodata = 0
    return nodata


# 栅格数据裁切掩膜处理：DEM数据 流向数据 汇流累积数据 河网数据 坡面和湖泊/水库范围数据 结果数据路径
def watershed_erase_area(dem_tif_path, dir_tif_path, acc_tif_path, stream_tif_path, water_s_s_tif_path, result_path):

    print("Erasing Mask Area from Dataset")

    # 获取数据集
    dem_old_ds = gdal.Open(dem_tif_path)
    dir_old_ds = gdal.Open(dir_tif_path)
    acc_old_ds = gdal.Open(acc_tif_path)
    stream_old_ds = gdal.Open(stream_tif_path)
    mask_ds = gdal.Open(water_s_s_tif_path)

    # 获取无数据标识
    dem_no_data = get_nodata_value(dem_old_ds)
    dir_no_data = get_nodata_value(dir_old_ds)
    acc_no_data = get_nodata_value(acc_old_ds)
    stream_no_data = get_nodata_value(stream_old_ds)
    mask_no_data = get_nodata_value(mask_ds)

    # 新数据路径
    dem_new_path = result_path + "/dem_erase.tif"
    dir_new_path = result_path + "/dir_erase.tif"
    acc_new_path = result_path + "/acc_erase.tif"
    stream_new_path = result_path + "/stream_erase.tif"

    # 创建结果数据
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    dem_new_ds = driver.CreateCopy(dem_new_path, dem_old_ds)
    dir_new_ds = driver.CreateCopy(dir_new_path, dir_old_ds)
    acc_new_ds = driver.CreateCopy(acc_new_path, acc_old_ds)
    stream_new_ds = driver.CreateCopy(stream_new_path, stream_old_ds)

    # 剔除掩膜区域处理
    for j in range(mask_ds.RasterYSize):
        for i in range(mask_ds.RasterXSize):
            mask_data = cu.get_raster_int_value(mask_ds, i, j)
            if mask_data != mask_no_data:
                # 处理DEM
                result_point = cu.off_transform(i, j, mask_ds, dem_new_ds)
                if cu.in_data(result_point[0], result_point[1], dem_new_ds.RasterXSize, dem_new_ds.RasterYSize):
                    cu.set_raster_float_value(dem_new_ds, result_point[0], result_point[1], dem_no_data)
                # 处理流向
                result_point = cu.off_transform(i, j, mask_ds, dir_new_ds)
                if cu.in_data(result_point[0], result_point[1], dir_new_ds.RasterXSize, dir_new_ds.RasterYSize):
                    cu.set_raster_int_value(dir_new_ds, result_point[0], result_point[1], int(dir_no_data))
                # 处理汇流累积量
                result_point = cu.off_transform(i, j, mask_ds, acc_new_ds)
                if cu.in_data(result_point[0], result_point[1], acc_new_ds.RasterXSize, acc_new_ds.RasterYSize):
                    cu.set_raster_float_value(acc_new_ds, result_point[0], result_point[1], acc_no_data)
                # 处理河网
                result_point = cu.off_transform(i, j, mask_ds, stream_new_ds)
                if cu.in_data(result_point[0], result_point[1], stream_new_ds.RasterXSize, stream_new_ds.RasterYSize):
                    cu.set_raster_int_value(stream_new_ds, result_point[0], result_point[1], int(stream_no_data))

    dem_old_ds = None
    dir_old_ds = None
    acc_old_ds = None
    stream_old_ds = None
    dem_new_ds = None
    dir_new_ds = None
    acc_new_ds = None
    stream_new_ds = None
    mask_ds = None

    return [dem_new_path, dir_new_path, acc_new_path, stream_new_path]


# 提取子流域入口函数：工作空间 高程数据路径 流向数据 汇流累积量数据 河网数据
def get_watershed(work_path, dem_tif_path, dir_tif_path, acc_tif_path, str_tif_path):

    # 提取子流域
    print("Stream Reach And Watershed")
    # 河网分级数据
    str_order_path = work_path + "/ord.tif"
    # 河网连接树文本
    str_tree_txt_path = work_path + "/tree.dat"
    # 河网投影列表
    str_coord_txt_path = work_path + "/coord.dat"
    # 河网矢量数据
    str_shp_path = work_path + "/stream_shp.shp"
    # 子流域数据
    ws_tif_path = work_path + "/river_sub-basin.tif"
    # 调用方法
    tu.stream_reach_and_watershed(dem_tif_path, dir_tif_path, acc_tif_path, str_tif_path, str_order_path,
                                  str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path)


# 提取考虑湖泊/水库的子流域结果： 工作空间 DEM数据 流向数据 汇流累积数据 河网数据 坡面和湖泊/水库范围数据
def watershed_extract(work_path, dem_tif_path, dir_tif_path, acc_tif_path, stream_tif_path, water_s_s_tif_path):
    # 创建过程数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 剔除考虑湖泊/水库的影响区域
    new_data_paths = watershed_erase_area(dem_tif_path, dir_tif_path, acc_tif_path, stream_tif_path, water_s_s_tif_path, work_path)

    # 提取处理后区域的子流域
    new_dem_path = new_data_paths[0]
    new_dir_path = new_data_paths[1]
    new_acc_path = new_data_paths[2]
    new_stream_path = new_data_paths[3]
    get_watershed(work_path, new_dem_path, new_dir_path, new_acc_path, new_stream_path)


if __name__ == '__main__':
    start = time.perf_counter()
    base_path = "D:/Graduation/Program/Data/14/test_erase_watershed"
    workspace_path = base_path + "/process"
    watershed_extract(workspace_path, base_path + "/dem_fill.tif", base_path + "/dir.tif", base_path + "/acc.tif",
                      base_path + "/stream.tif", base_path + "/water_slope.tif")
    end = time.perf_counter()
    print('Run', end - start, 's')
