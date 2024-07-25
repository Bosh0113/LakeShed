# coding=utf-8
import os
import time
import gdal
import common_utils as cu


def record_rivers(work_path, river_tif_path, acc_tif_path):
    # 创建结果数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 创建数据集
    river_ds = gdal.Open(river_tif_path)
    acc_ds = gdal.Open(acc_tif_path)

    # 创建河流记录文件
    river_record_txt = work_path + "/river_record.txt"
    if os.path.exists(river_record_txt):
        os.remove(river_record_txt)

    print("Recording rivers...")

    # 记录河流信息到文件
    with open(river_record_txt, 'a') as river_f:
        for i in range(river_ds.RasterYSize):
            for j in range(river_ds.RasterXSize):
                # 获取river中该点的值
                river_value = cu.get_raster_int_value(river_ds, j, i)
                # 判断是否为河流
                if river_value == 1:
                    # 需要记录的河系信息：x索引，y索引，汇流累积量
                    river_cell_acc = cu.get_raster_float_value(acc_ds, j, i)
                    river_record_item = [j, i, river_cell_acc]
                    # 记录到文件中
                    river_record_str = ','.join(str(k) for k in river_record_item)
                    river_f.write(river_record_str + '\n')

    print("File write over.")


if __name__ == '__main__':
    start = time.perf_counter()
    base_path = "D:/Graduation/Program/Data/9/process"
    workspace_path = base_path + "/result"
    record_rivers(workspace_path, base_path + "/stream.tif", base_path + "/acc.tif")
    end = time.perf_counter()
    print('Run', end - start, 's')
