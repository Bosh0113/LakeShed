# coding=utf-8
import os
import geopandas as gpd
import time


# 矢量裁切矢量(shp): 被裁数据 范围数据
def clip_shp(o_shp, mask_shp, result_shp):
    o_rf = gpd.read_file(o_shp)
    m_rf = gpd.read_file(mask_shp)
    r_rf = gpd.clip(o_rf, m_rf)
    r_rf.to_file(result_shp)


# 根据面积筛选大于阈值的元组: 原始shp路径 结果路径 面积阈值
def filter_by_area(shp_path, res_path, area):
    shp_rf = gpd.read_file(shp_path)
    result = shp_rf[shp_rf['Lake_area'].astype(float) > area]
    result.to_file(res_path)


# 根据范围和面积大小过滤出湖泊: 原始湖泊数据(shp) 范围数据(shp) 结果数据路径(shp) 面积阈值(单位km2，可选)
def filter_lakes_extent_area(o_lake_shp, extent_shp, result_shp, area=0.1):
    o_rf = gpd.read_file(o_lake_shp)
    m_rf = gpd.read_file(extent_shp)
    r_rf = o_rf[o_rf['Lake_area'].astype(float) > area]
    result = gpd.clip(r_rf, m_rf)
    result.to_file(result_shp)
