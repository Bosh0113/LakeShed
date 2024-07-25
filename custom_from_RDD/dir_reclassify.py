# coding=utf-8
import time
import rasterio
import os

# 重分类工具: 原始数据路径 分类后数据路径
# 分类表:
# 1、原始流向数据转8制(TauDEM)
# 2、原始流向数据128制标准化(pfaf用)
def reclassify_dir(input_file, output_file):
    print("Dir Reclassify...")
    with rasterio.open(input_file) as src:
        profile = src.profile
        dir_o = src.read()
        dir_o[dir_o==8]=6
        dir_o[dir_o==2]=8
        dir_o[dir_o==4]=7
        dir_o[dir_o==16]=5
        dir_o[dir_o==32]=4
        dir_o[dir_o==64]=3
        dir_o[dir_o==128]=2
        dir_o[dir_o==247]=0
        dir_o[dir_o==255]=0
    
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(dir_o)