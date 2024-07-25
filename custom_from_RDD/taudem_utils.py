# coding=utf-8
import os

# TauDEM路径
taudem_path = '/disk1/software/package/TauDEM-5.3.7/src/build'


# 填洼：DEM(input) 填洼后的DEM(output)
def pit_remove(dem_tif_path, dem_filled_path):
    print("Pit Remove")
    # cmd语句调用TauDEM的Pit Remove程序
    dem_cmd = 'mpiexec -n ' + str(5) + ' ' + taudem_path + '/pitremove -z ' + dem_tif_path + ' -fel ' + dem_filled_path
    print(dem_cmd)
    d = os.system(dem_cmd)
    print(d)


# 计算流向：DEM(input) 流向(output) 坡度(output)
def d8_flow_directions(dem_tif_path, dir_tif_path, slope_output_path):
    print("D8 Flow Directions")
    # cmd语句调用TauDEM的D8 Flow Directions程序
    dir_cmd = 'mpiexec -n ' + str(5) + ' ' + taudem_path + '/d8flowdir -fel ' + dem_tif_path + ' -p ' + \
              dir_tif_path + ' -sd8 ' + slope_output_path
    print(dir_cmd)
    d = os.system(dir_cmd)
    print(d)


# 计算贡献区：流向(input) 贡献区(output) [边界污染(optional)](默认不考虑)
def d8_contributing_area(dir_tif_path, contributing_area_path, nc=0):
    print("D8 Contributing Area")
    # cmd语句调用TauDEM的D8 Contributing Area程序
    if nc == 0:
        con_cmd = 'mpiexec -np ' + str(4) + ' ' + taudem_path + '/aread8 -p ' + dir_tif_path + ' -ad8 ' + \
                  contributing_area_path + ' -nc'
    else:
        con_cmd = 'mpiexec -np ' + str(4) + ' ' + taudem_path + '/aread8 -p ' + dir_tif_path + ' -ad8 ' + \
                  contributing_area_path
    print(con_cmd)
    d = os.system(con_cmd)
    print(d)


# 计算汇流累积量：流向(input) 最长流长(output) 总流长(output) 河流分级(output)
def grid_network(dir_tif_path, longest_upstream_path, total_upstream_path, str_order_acc_path):
    print("Grid Network")
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    acc_cmd = 'mpiexec -n ' + str(5) + ' ' + taudem_path + '/gridnet -p ' + dir_tif_path + ' -plen ' + \
              longest_upstream_path + ' -tlen ' + total_upstream_path + ' -gord ' + str_order_acc_path
    print(acc_cmd)
    d = os.system(acc_cmd)
    print(d)


# 提取河流：汇流累积量(input) 河流(output) 提取阈值(input)
def stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold):
    print("Stream Definition By Threshold")
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    str_cmd = 'mpiexec -n ' + str(5) + ' ' + taudem_path + '/threshold -ssa ' + total_upstream_path + \
              ' -src ' + str_tif_path + ' -thresh ' + extract_threshold
    print(str_cmd)
    d = os.system(str_cmd)
    print(d)


# 提取子流域： DEM(input) 流向(input) 贡献区(input) 河流(input) 河流分级(output) 河流树状记录(output) 河流坐标(output)
# 矢量河流(output) 子流域(output)
def stream_reach_and_watershed(dem_tif_path, dir_tif_path, contributing_area_path, str_tif_path, str_order_path,
                               str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path):
    print("Stream Reach And Watershed")
    # cmd语句调用TauDEM的Stream Reach And Watershed程序
    ws_cmd = 'mpiexec -n ' + str(5) + ' ' + taudem_path + '/streamnet -fel ' + dem_tif_path + ' -p ' + \
             dir_tif_path + ' -ad8 ' + contributing_area_path + ' -src ' + str_tif_path + ' -ord ' + \
             str_order_path + ' -tree ' + str_tree_txt_path + ' -coord ' + str_coord_txt_path + ' -net ' + \
             str_shp_path + ' -w ' + ws_tif_path
    print(ws_cmd)
    d = os.system(ws_cmd)
    print(d)
