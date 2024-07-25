# coding=utf-8
import gdal
import ogr
import os


# 计算shp对应在tif的左上角坐标和像元个数: tif的左上角坐标 像元大小 shp范围
def shp_geo_transform(tif_lt_point, cell_size, shp_extent):
    tif_left = tif_lt_point[0]
    tif_top = tif_lt_point[1]

    extent = list(shp_extent)
    left = extent[0]
    right = extent[1]
    bottom = extent[2]
    top = extent[3]

    left_dif = abs((tif_left - left) % cell_size)
    right_dif = abs((tif_left - right) % cell_size)
    bottom_dif = abs((tif_top - bottom) % cell_size)
    top_dif = abs((tif_top - top) % cell_size)

    new_left = left - (cell_size - left_dif)
    new_right = right + right_dif
    new_bottom = bottom - (cell_size - bottom_dif)
    new_top = top + top_dif

    width = new_right - new_left
    height = new_bottom - new_top

    raster_x_num = abs(int(width/cell_size)) + 1
    raster_y_num = abs(int(height/cell_size)) + 1

    new_geo_transform = tuple([new_left, cell_size, 0.0, new_top, 0.0, -cell_size])

    return new_geo_transform, raster_x_num, raster_y_num


# lake的shp文件栅格化: shp文件路径 参考Raster文件路径 结果输出路径 结果范围参考(默认参考tif)
def lake_rasterize(shp_path, raster_path, result_path, value, no_data, shp_ex=0):
    print("Shapefile Rasterize.")

    ra_ds = gdal.Open(raster_path)
    shp = ogr.Open(shp_path, 0)
    shp_layer = shp.GetLayerByIndex(0)

    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geo_transform = ra_ds.GetGeoTransform()
    raster_x_size = ra_ds.RasterXSize
    raster_y_size = ra_ds.RasterYSize

    if shp_ex:
        # 得到范围分别为：left right bottom top
        shp_extent = shp_layer.GetExtent()
        full_geo_transform, raster_x_size, raster_y_size = shp_geo_transform([full_geo_transform[0], full_geo_transform[3]], full_geo_transform[1], shp_extent)

    re_ds = driver.Create(result_path, raster_x_size, raster_y_size, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
    re_ds.SetGeoTransform(full_geo_transform)
    re_ds.SetProjection(ra_ds.GetProjection())
    re_ds.GetRasterBand(1).SetNoDataValue(int(no_data))

    # gdal.RasterizeLayer(re_ds, [1], shp_layer, options=["ATTRIBUTE=value"])
    gdal.RasterizeLayer(re_ds, [1], shp_layer, burn_values=[int(value)])

    ra_ds = None
    re_ds = None
    shp.Release()


if __name__ == '__main__':
    workspace = "G:/Graduation/Program/Data/31/2"
    shp_data = workspace + "/lakes_vec.shp"
    raster_data = workspace + "/dir.tif"
    result_path = workspace + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    result_data = result_path + "/lakes_raster.tif"
    lake_rasterize(shp_data, raster_data, result_data, -99, -9)
