# coding=utf-8
import struct
import geopandas
import gdal


# 获取栅格数据值(signed int)：数据集 x索引 y索引
def get_raster_int_value(dataset, x, y):
    return int.from_bytes(dataset.GetRasterBand(1).ReadRaster(x, y, 1, 1), 'little', signed=True)


# 获取栅格数据值(unsigned int)：数据集 x索引 y索引
def get_raster_un_int_value(dataset, x, y):
    return int.from_bytes(dataset.GetRasterBand(1).ReadRaster(x, y, 1, 1), 'little', signed=False)


# 获取栅格数据值(float)： 数据集 x索引 y索引
def get_raster_float_value(dataset, x, y):
    return struct.unpack('f', dataset.GetRasterBand(1).ReadRaster(x, y, 1, 1))[0]


# 写入栅格数据值：数据集 x索引 y索引 值
def set_raster_int_value(dataset, x, y, value):
    dataset.GetRasterBand(1).WriteRaster(x, y, 1, 1, struct.pack("i", value))


# 写入栅格数据值(float)：数据集 x索引 y索引 值
def set_raster_float_value(dataset, x, y, value):
    dataset.GetRasterBand(1).WriteRaster(x, y, 1, 1, struct.pack("f", value))


# 判断是否超出数据范围：x索引 y索引 x最大值 y最大值
def in_data(x, y, x_size, y_size):
    # 左侧超出
    if x < 0:
        return False
    # 上方超出
    if y < 0:
        return False
    # 右侧超出
    if x >= x_size:
        return False
    # 下方超出
    if y >= y_size:
        return False
    return True


# 根据流向得到指向的栅格索引(8制)
def get_to_point(x, y, dir_8):
    if dir_8 == 1:
        return [x + 1, y]
    elif dir_8 == 8:
        return [x + 1, y + 1]
    elif dir_8 == 7:
        return [x, y + 1]
    elif dir_8 == 6:
        return [x - 1, y + 1]
    elif dir_8 == 5:
        return [x - 1, y]
    elif dir_8 == 4:
        return [x - 1, y - 1]
    elif dir_8 == 3:
        return [x, y - 1]
    elif dir_8 == 2:
        return [x + 1, y - 1]
    else:
        return []


# 根据流向得到指向的栅格索引(128制)
def get_to_point_128(x, y, dir_128):
    dir_128 = abs(dir_128)
    if dir_128 == 1:
        return [x + 1, y]
    elif dir_128 == 2:
        return [x + 1, y + 1]
    elif dir_128 == 4:
        return [x, y + 1]
    elif dir_128 == 8:
        return [x - 1, y + 1]
    elif dir_128 == 16:
        return [x - 1, y]
    elif dir_128 == 32:
        return [x - 1, y - 1]
    elif dir_128 == 64:
        return [x, y - 1]
    elif dir_128 == 128:
        return [x + 1, y - 1]
    else:
        return []


# 返回8个方向的索引
def get_8_dir(x, y):
    return [[x - 1, y - 1],
            [x, y - 1],
            [x + 1, y - 1],
            [x - 1, y],
            [x + 1, y],
            [x - 1, y + 1],
            [x, y + 1],
            [x + 1, y + 1]]


# 返回8个方向的坐标: 像元左上角x坐标 像元左上角y坐标 像元x距离 像元y距离
def get_8_dir_coord(x, y, x_size, y_size):
    return [[x - x_size, y - y_size],
            [x, y - y_size],
            [x + x_size, y - y_size],
            [x - x_size, y],
            [x + x_size, y],
            [x - x_size, y + y_size],
            [x, y + y_size],
            [x + x_size, y + y_size]]


# 根据数据集索引计算坐标: 原索引对 数据集 坐标对(返回)
def off_to_coord(o_off, data_ds):
    # 获取数据集信息
    o_geotransform = data_ds.GetGeoTransform()

    # 获取该点x,y坐标
    x_coord = o_geotransform[0] + o_off[0] * o_geotransform[1] + o_off[1] * o_geotransform[2]
    y_coord = o_geotransform[3] + o_off[0] * o_geotransform[4] + o_off[1] * o_geotransform[5]

    return [x_coord, y_coord]


# 根据坐标和数据集计算索引: 坐标对 数据集 索引对(返回)
def coord_to_off(o_coord, data_ds):
    # 获取数据集信息
    n_geotransform = data_ds.GetGeoTransform()
    # 获取该点在river中的索引
    n_xoff = int((o_coord[0] - n_geotransform[0]) / n_geotransform[1] + 0.5)
    n_yoff = int((o_coord[1] - n_geotransform[3]) / n_geotransform[5] + 0.5)
    return [n_xoff, n_yoff]


# 转换不同数据集的索引: 原x索引 原y索引 原数据集 新数据集 新数据索引(返回)
def off_transform(o_xoff, o_yoff, o_dataset, n_dataset):
    n_coord = off_to_coord([o_xoff, o_yoff], o_dataset)
    n_off = coord_to_off(n_coord, n_dataset)
    return n_off


# 复制tif数据到新路径
def copy_tif_data(old_path, copy_path):
    old_ds = gdal.Open(old_path)
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    copy_ds = driver.CreateCopy(copy_path, old_ds)
    old_ds = None
    copy_ds = None


# 重分类：原数据路径 重分类数据路径 需要更新的像元值数组(二维数组) 新像元值数组(一维数组)
def tif_reclassify(old_tif_path, updated_tif_path, update_value_2array, new_value_array):
    old_ds = gdal.Open(old_tif_path)
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    copy_ds = driver.CreateCopy(updated_tif_path, old_ds)
    for j in range(copy_ds.RasterYSize):
        for i in range(copy_ds.RasterXSize):
            data_value = get_raster_int_value(copy_ds, i, j)
            for k in range(0, len(update_value_2array), 1):
                if data_value in update_value_2array[k]:
                    new_value = new_value_array[k]
                    set_raster_int_value(copy_ds, i, j, new_value)
                    break
    old_ds = None
    copy_ds = None


# 栅格数据裁切掩膜处理：原始数据 掩膜数据 结果数据
def raster_erase_mask(raster_path, mask_path, result_path, data_type="int"):
    # 获取数据集
    old_ds = gdal.Open(raster_path)
    mask_ds = gdal.Open(mask_path)
    # 获取无数据标识
    old_no_data = old_ds.GetRasterBand(1).GetNoDataValue()
    mask_no_data = mask_ds.GetRasterBand(1).GetNoDataValue()
    # 创建结果数据
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    result_ds = driver.CreateCopy(result_path, old_ds)
    # 掩膜处理
    for j in range(mask_ds.RasterYSize):
        for i in range(mask_ds.RasterXSize):
            mask_data = get_raster_int_value(mask_ds, i, j)
            if mask_data != mask_no_data:
                result_point = off_transform(i, j, mask_ds, result_ds)
                if in_data(result_point[0], result_point[1], result_ds.RasterXSize, result_ds.RasterYSize):
                    if data_type == "int":
                        set_raster_int_value(result_ds, result_point[0], result_point[1], int(old_no_data))
                    if data_type == "float":
                        set_raster_float_value(result_ds, result_point[0], result_point[1], old_no_data)
    old_ds = None
    result_ds = None


# 判断索引的像元是否为湖泊/水库：湖泊水库数据集 x索引 y索引
def is_water_cell(water_dataset, xoff, yoff, water_value):
    # 判断是否在water数据中
    judge_in_data = in_data(xoff, yoff, water_dataset.RasterXSize, water_dataset.RasterYSize)
    # 如果在water数据内
    if judge_in_data:
        # 获取water内像元值
        water_data_value = get_raster_int_value(water_dataset, xoff, yoff)
        # 如果像元为湖泊/水库则判断当前河流像元是否与湖泊/水库邻接
        if water_data_value == water_value:
            return 1
    return 0


# shapefile转geojson: shapefile路径 geojson路径
def shp_to_geojson(shp_path, geoj_path):
    shp = geopandas.read_file(shp_path)
    shp.to_file(geoj_path, driver="GeoJSON", encoding="utf-8")


# geojson转shapefile: geojson路径 shapefile路径
def geojson_to_shp(geoj_path, shp_path):
    geoj = geopandas.read_file(geoj_path)
    geoj.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")


# 根据两点索引求流向值
def dir_between_points(from_point, to_point):
    for dir_value in range(1, 9, 1):
        if get_to_point(from_point[0], from_point[1], dir_value) == to_point:
            return dir_value
