# coding=utf-8
import common_utils as cu
import gdal
import os


# 提取陆地上入流到海洋的像元: yamazaki流向数据重分类后的数据 yamazaki流向原数据 流入海岸线的第一级陆上像元集合
def get_trace_points(dir_tif, flag_tif, trace_tif, seaside_txt=None, final_txt=None):

    coastline_value = 0
    final_value = -1

    dir_ds = gdal.Open(dir_tif)
    f_ds = gdal.Open(flag_tif)

    # 创建trace start数据
    print("Create Trace file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = dir_ds.GetGeoTransform()
    trace_ds = driver.Create(trace_tif, dir_ds.RasterXSize, dir_ds.RasterYSize, 1, gdal.GDT_Byte, options=['COMPRESS=DEFLATE'])
    trace_ds.SetGeoTransform(full_geotransform)
    trace_ds.SetProjection(dir_ds.GetProjection())
    trace_ds.GetRasterBand(1).SetNoDataValue(0)

    # 创建记录文件
    seaside_flag = 0
    seaside_f = None
    if seaside_txt is not None:
        print("Record Final Points.")
        seaside_flag = 1
        if os.path.exists(seaside_txt):
            os.remove(seaside_txt)
    if seaside_flag:
        seaside_f = open(seaside_txt, "a")

    final_flag = 0
    final_f = None
    if final_txt is not None:
        print("Record Final Points.")
        final_flag = 1
        if os.path.exists(final_txt):
            os.remove(final_txt)
    if final_flag:
        final_f = open(final_txt, "a")

    # 遍历基础数据记录seaside
    print("Get Trace Data...")
    for i in range(f_ds.RasterYSize):
        for j in range(f_ds.RasterXSize):
            # 获取流向的值
            flag_value = cu.get_raster_int_value(f_ds, j, i)
            # 如果是coastline
            if flag_value == coastline_value:
                # 获取周边像元索引
                neibor_cells = cu.get_8_dir(j, i)
                # 遍历
                for n_cell in neibor_cells:
                    # 判断是否在数据内
                    in_data = cu.in_data(n_cell[0], n_cell[1], dir_ds.RasterXSize, dir_ds.RasterYSize)
                    # 若在数据内
                    if in_data:
                        # 获取流向值
                        dir_value = cu.get_raster_int_value(dir_ds, n_cell[0], n_cell[1])
                        # 获取流向的像元索引
                        n_to_point = cu.get_to_point(n_cell[0], n_cell[1], dir_value)
                        # 若为当前上游像元
                        if n_to_point == [j, i]:
                            # 记录为seaside
                            cu.set_raster_int_value(trace_ds, n_cell[0], n_cell[1], 1)
                            # 记录到文件
                            if seaside_flag:
                                # 获得栅格像元左上角坐标
                                seaside_record_item = cu.off_to_coord([j, i], f_ds)
                                seaside_record_str = ','.join(str(k) for k in seaside_record_item)
                                seaside_f.write(seaside_record_str + '\n')
            # 如果是final point
            elif flag_value == final_value:
                # 记录为final points
                cu.set_raster_int_value(trace_ds, j, i, 1)
                # 记录到文件
                if final_flag:
                    final_record_item = cu.off_to_coord([j, i], f_ds)
                    final_record_str = ','.join(str(k) for k in final_record_item)
                    final_f.write(final_record_str + '\n')
    dir_ds = None
    f_ds = None
    trace_ds = None
    seaside_f = None
    final_f = None