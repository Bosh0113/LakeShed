# coding=utf-8
import os
import time
import gdal
import taudem_utils as tu
import common_utils as cu
import record_rivers as rr

water_value = -99


# 结合河流修正湖泊/水库边界：湖泊/水库数据路径 河网数据路径 流向数据路径
def water_revise(water_tif_path, river_tif_path, river_record_path, dir_tif_path):
    global water_value

    # 创建数据集
    water_ds = gdal.OpenEx(water_tif_path, 1)
    river_ds = gdal.Open(river_tif_path)
    dir_ds = gdal.Open(dir_tif_path)

    # 河流在water中的索引数组
    river_in_water_data = []

    # 遍历水体数据搜索范围内河流
    # for i in range(water_ds.RasterYSize):
    #     for j in range(water_ds.RasterXSize):
    #         # 获取该点x,y在river中的索引
    #         river_off = cu.off_transform(j, i, water_ds, river_ds)
    #         # 若在数据内
    #         if cu.in_data(river_off[0], river_off[1], river_ds.RasterXSize, river_ds.RasterYSize):
    #             # 获取river中该点的值
    #             river_value = cu.get_raster_int_value(river_ds, river_off[0], river_off[1])
    #             # 判断是否为河流
    #             if river_value == 1:
    #                 # 记录河流在water中的索引
    #                 river_in_water_data.append([j, i])

    # 读取河系信息记录水体数据范围内河流索引
    with open(river_record_path, 'r') as river_file:
        for line in river_file.readlines():
            river_info_str = line.strip('\n')
            river_info = river_info_str.split(',')
            # 将river像元的x,y索引
            river_xoff = int(river_info[0])
            river_yoff = int(river_info[1])
            # 得到在水域中对应的索引
            river_off_w = cu.off_transform(river_xoff, river_yoff, river_ds, water_ds)
            # 若在数据内
            if cu.in_data(river_off_w[0], river_off_w[1], water_ds.RasterXSize, water_ds.RasterYSize):
                # 记录河流在water中的索引
                river_in_water_data.append(river_off_w)

    # 根据与河流的邻近关系更新水体边界
    update_flag = 1
    while update_flag:
        # 标记是否更新完成
        update_flag = 0
        print("Update...")
        # 根据水体与河流邻接更新水体
        for index in range(len(river_in_water_data)):
            river_in_water_x = river_in_water_data[index][0]
            river_in_water_y = river_in_water_data[index][1]
            # 获取该点在water中的值
            water_data_value = cu.get_raster_int_value(water_ds, river_in_water_x, river_in_water_y)
            # 判断若不在水体内
            if water_data_value != water_value:
                # 获取该点x,y在river中的索引
                river_off = cu.off_transform(river_in_water_x, river_in_water_y, water_ds, river_ds)
                # 获取该处流向
                dir_off = cu.off_transform(river_in_water_x, river_in_water_y, water_ds, dir_ds)
                dir_value = cu.get_raster_int_value(dir_ds, dir_off[0], dir_off[1])
                # 获取该处在river的下一个像元索引
                to_river_point = cu.get_to_point(river_off[0], river_off[1], dir_value)
                # 判断是否能得到下游（应对内流区问题）
                if len(to_river_point) > 0:
                    # 获取该点在water中的索引
                    w_n_off = cu.off_transform(to_river_point[0], to_river_point[1], river_ds, water_ds)
                    to_point_is_water = cu.is_water_cell(water_ds, w_n_off[0], w_n_off[1], water_value)
                    if to_point_is_water:
                        # 若当前像元与下游像元x相同
                        if river_in_water_x == w_n_off[0]:
                            # 判断当前像元y方向上下是否为湖泊/水库
                            r_in_w_n0_is_water = cu.is_water_cell(water_ds, river_in_water_x - 1, river_in_water_y, water_value)
                            r_in_w_n1_is_water = cu.is_water_cell(water_ds, river_in_water_x + 1, river_in_water_y, water_value)
                            if r_in_w_n0_is_water or r_in_w_n1_is_water:
                                # 更新water此处为湖泊/水库
                                cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                                update_flag = 1
                        # 若当前像元与下游像元y相同
                        elif river_in_water_y == w_n_off[1]:
                            # 判断当前像元x方向上下是否为湖泊/水库
                            r_in_w_n0_is_water = cu.is_water_cell(water_ds, river_in_water_x, river_in_water_y - 1, water_value)
                            r_in_w_n1_is_water = cu.is_water_cell(water_ds, river_in_water_x, river_in_water_y + 1, water_value)
                            if r_in_w_n0_is_water or r_in_w_n1_is_water:
                                # 更新water此处为湖泊/水库
                                cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                                update_flag = 1
                        # 若当前像元与下游像元不在xy轴共线
                        else:
                            # 判断两像元公共邻接像元是否为湖泊/水库
                            r_in_w_n0_is_water = cu.is_water_cell(water_ds, river_in_water_x, w_n_off[1], water_value)
                            r_in_w_n1_is_water = cu.is_water_cell(water_ds, w_n_off[0], river_in_water_y, water_value)
                            if r_in_w_n0_is_water or r_in_w_n1_is_water:
                                # 更新water此处为湖泊/水库
                                cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                                update_flag = 1

    print("Over.")
    water_ds = None
    river_ds = None
    dir_ds = None


# 河流修正入口函数：工作空间路径 高程数据路径 水体数据路径
def water_revise_prepare(work_path, dem_tif_path, water_tif_path, extract_threshold):

    # 创建结果数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 计算流向
    print("D8 Flow Directions")
    # 流向数据
    dir_tif_path = work_path + "/dir.tif"
    # 斜率
    slope_output_path = work_path + "/slopes.tif"
    # 调用方法
    tu.d8_flow_directions(dem_tif_path, dir_tif_path, slope_output_path)

    # 计算汇流累积量
    print("Grid Network")
    # 上游最长流长
    longest_upstream_path = work_path + "/longest_flow.tif"
    # 上游总流长，即汇流累积量
    total_upstream_path = work_path + "/acc.tif"
    # 河网分级数据
    str_order_acc_path = work_path + "/ord_acc.tif"
    # 调用方法
    tu.grid_network(dir_tif_path, longest_upstream_path, total_upstream_path, str_order_acc_path)

    # 提取河流
    print("Stream Definition By Threshold")
    # 河网数据
    str_tif_path = work_path + "/stream.tif"
    # 提取阈值
    extract_threshold = str(extract_threshold)
    # 调用方法
    tu.stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold)

    # 记录河流信息
    rr.record_rivers(work_path, work_path + "/stream.tif", work_path + "/acc.tif")

    # 新建结果数据
    water_copy_path = work_path + '/lake.tif'
    cu.copy_tif_data(water_tif_path, water_copy_path)

    # 修正水体
    water_revise(water_copy_path, work_path + "/stream.tif", work_path + "/river_record.txt", dir_tif_path)

