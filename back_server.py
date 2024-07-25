from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import time
import shutil
import zipfile

# import modelDataWork as mdw

app = Flask(__name__)
app.config['TASK_FOLDER'] = 'static/tasks'


@app.route('/main')
def mainpage():
    return app.send_static_file("main.html")


# 自定义参数提取结果
@app.route('/runResetData', methods=['POST'])
def runResetData():
    riverThreshold = request.form.get('riverThreshold')
    lakeThreshold = request.form.get('lakeThreshold')
    extentGeojson_str = request.form.get('extentGeojson')
    
    print('extentGeojson_str')
    print(extentGeojson_str)

    run_id = str(time.time())
    comp_folder = os.path.join(os.path.abspath('.'), app.config['TASK_FOLDER'], run_id)
    if not os.path.exists(comp_folder):
        os.makedirs(comp_folder)
    
    extent_geojson_path = os.path.join(comp_folder, 'extent.geojson')
    with open(extent_geojson_path, 'w') as w:
        w.write(str(extentGeojson_str))

    cmd = 'python3 ' + os.path.abspath('.')+'/custom_from_RDD/__init__.py ' + comp_folder + ' ' + extent_geojson_path + ' ' + riverThreshold + ' ' + lakeThreshold
    d = os.system(cmd)
    print("CMD status", d)

    shutil.make_archive(comp_folder, 'zip', comp_folder)

    shutil.rmtree(comp_folder)

    result_zip = "/" + app.config['TASK_FOLDER'] + "/" + run_id + '.zip'

    return result_zip


# 自定义生成提取结果
@app.route('/runCustomData', methods=['POST'])
def runCustomData():
    f_dem = request.files['fileDEM']
    f_lake = request.files['fileLake']
    threshold = request.form.get('threshold')

    run_id = str(time.time())
    comp_folder = os.path.join(os.path.abspath('.'), app.config['TASK_FOLDER'], run_id)
    if not os.path.exists(comp_folder):
        os.makedirs(comp_folder)

    f_dem_path = os.path.join(comp_folder,secure_filename(f_dem.filename))
    f_lake_path = os.path.join(comp_folder,secure_filename(f_lake.filename))
    f_dem.save(f_dem_path)
    f_lake.save(f_lake_path)

    with zipfile.ZipFile(f_lake_path, 'r') as zip_ref:
        zip_ref.extractall(comp_folder)
    
    dem_tif_filename = None
    lake_shp_filename = None
    file_list = os.listdir(comp_folder)
    for filename in file_list:
        if filename[-4:]=='.tif':
            dem_tif_filename = os.path.join(comp_folder, filename)
        if filename[-4:]=='.shp':
            lake_shp_filename = os.path.join(comp_folder, filename)

    cmd = 'python3 ' + os.path.abspath('.')+'/custom_by_upload/__init__.py ' + comp_folder + ' ' + dem_tif_filename + ' ' + lake_shp_filename + ' ' + threshold
    d = os.system(cmd)
    print("CMD status", d)

    shutil.make_archive(comp_folder, 'zip', comp_folder)

    shutil.rmtree(comp_folder)

    result_zip = "/" + app.config['TASK_FOLDER'] + "/" + run_id + '.zip'

    return result_zip


if __name__ == "__main__":
    app.run('0.0.0.0', 5002)