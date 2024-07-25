# coding=utf-8
import os
import time
import taudem_utils as tu


# 计算流向和汇流累积数据：高程数据路径 流向数据路径 汇流累积量数据路径
def get_dir_acc(work_path, dem_tif_path, dir_tif_path, acc_tif_path):

    # 创建结果数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 计算流向
    print("D8 Flow Directions")
    # 流向数据
    dir_path = dir_tif_path
    # 斜率
    slope_output_path = work_path + "/slopes.tif"
    # 调用方法
    tu.d8_flow_directions(dem_tif_path, dir_path, slope_output_path)

    # 计算共享区
    print("D8 Contributing Area")
    # D8贡献区数据
    contributing_area_path = acc_tif_path
    # 调用方法
    tu.d8_contributing_area(dir_tif_path, contributing_area_path)


# 此程序可用cmd调用python执行
# 提取子流域为tif，过程数据中包含河网的tif和shp类型数据
if __name__ == '__main__':
    start = time.perf_counter()
    base_path = "D:/Graduation/Program/Data/14"
    workspace_path = base_path + "/test_dir_acc"
    get_dir_acc(workspace_path, base_path + "/dem_fill.tif", workspace_path + "/dir.tif", workspace_path + "/acc.tif")
    end = time.perf_counter()
    print('Run', end - start, 's')
