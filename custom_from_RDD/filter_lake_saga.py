# coding=utf-8
import time
import os


# 可执行文件所在路径
saga_cmd = "saga_cmd"


def clip_shp(clip_extent, o_file, result):
    print("Filter Lakes...")
    cmd = saga_cmd + " shapes_polygons 11 -CLIP " + clip_extent + " -S_INPUT " + o_file + " -M_INPUT " + o_file + " -S_OUTPUT " + result + " -M_OUTPUT " + result
    print(cmd)
    d = os.system(cmd)
    print(d)