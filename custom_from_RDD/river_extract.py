import os
import time
import taudem_utils as tu


# 根据阈值提取河道：工作空间 汇流累积量 提取阈值
def get_river(work_path, acc_tif_path, river_threshold):
    # 创建结果文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)
    # 结果数据路径
    river_tif_path = work_path + "/stream.tif"
    # 调用TauDEM的Threshold程序
    tu.stream_definition_by_threshold(acc_tif_path, river_tif_path, str(river_threshold))