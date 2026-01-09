import os
import gc
import base64
import io
import numpy as np
import cv2
import ezdxf
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'temp'
MAX_WIDTH = 2000 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def clean_memory(*arrays):
    """显式释放 numpy 数组内存"""
    for arr in arrays:
        if arr is not None:
            del arr
    gc.collect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_preview', methods=['POST'])
def process_preview():
    """预览接口逻辑保持不变，主要用于二值化处理"""
    try:
        file = request.files['image']
        threshold = int(request.form.get('threshold', 128))
        invert = request.form.get('invert') == 'true'
        single_line = request.form.get('single_line') == 'true'
        ignore_border = request.form.get('ignore_border') == 'true'
        fill_color = request.form.get('fill_color', 'none')

        in_memory_file = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(in_memory_file, cv2.IMREAD_COLOR)
        
        # 缩放
        h, w = img.shape[:2]
        if w > MAX_WIDTH:
            scale = MAX_WIDTH / w
            img = cv2.resize(img, (MAX_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA)
            final_h, final_w = img.shape[:2]
        else:
            final_h, final_w = h, w

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if invert:
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        else:
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # 忽略边缘处理
        if ignore_border:
            # 添加白色边框，将主体内容与图像边缘分离
            border_size = 10
            # 使用白色填充边框
            binary = cv2.copyMakeBorder(binary, border_size, border_size, border_size, border_size, 
                                      cv2.BORDER_CONSTANT, value=255)
            # 记录新的尺寸
            final_h, final_w = binary.shape[:2]

        # 单线条模式处理 - 减小线条之间的缝隙
        if single_line:
            # 使用膨胀操作增加线条厚度，减小缝隙
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            # 先膨胀增加线条厚度
            binary = cv2.dilate(binary, kernel, iterations=1)
            # 然后进行形态学开操作平滑轮廓
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        _, buffer = cv2.imencode('.png', binary)
        img_str = base64.b64encode(buffer).decode('utf-8')

        clean_memory(img, gray, binary, in_memory_file)
        return jsonify({'status': 'success', 'image': img_str})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/convert_dxf', methods=['POST'])
def convert_dxf():
    """使用 OpenCV 轮廓检测进行矢量化"""
    try:
        file = request.files['image']
        threshold = int(request.form.get('threshold', 128))
        invert = request.form.get('invert') == 'true'
        single_line = request.form.get('single_line') == 'true'
        ignore_border = request.form.get('ignore_border') == 'true'
        fill_color = request.form.get('fill_color', 'none')

        in_memory_file = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(in_memory_file, cv2.IMREAD_COLOR)

        h, w = img.shape[:2]
        if w > MAX_WIDTH:
            scale = MAX_WIDTH / w
            img = cv2.resize(img, (MAX_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA)
            final_h, final_w = img.shape[:2]
        else:
            final_h, final_w = h, w

        # 1. 预处理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if invert:
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        else:
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # 忽略边缘处理
        if ignore_border:
            # 添加白色边框，将主体内容与图像边缘分离
            border_size = 10
            # 使用白色填充边框
            binary = cv2.copyMakeBorder(binary, border_size, border_size, border_size, border_size, 
                                      cv2.BORDER_CONSTANT, value=255)
            # 记录新的尺寸
            final_h, final_w = binary.shape[:2]

        # 单线条模式处理 - 减小线条之间的缝隙
        if single_line:
            # 使用膨胀操作增加线条厚度，减小缝隙
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            # 先膨胀增加线条厚度
            binary = cv2.dilate(binary, kernel, iterations=1)
            # 然后进行形态学开操作平滑轮廓
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # 2. 使用 OpenCV 查找轮廓 - 提取所有轮廓（包括内部）并保留所有细节
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        # 3. 生成 DXF
        doc = ezdxf.new('R2000')
        msp = doc.modelspace()
        doc.layers.new('OPENCV_OUTLINE', dxfattribs={'color': 7})

        total_curves = 0

        # 遍历所有轮廓
        for contour in contours:
            # 将轮廓转换为点列表
            points = []
            for point in contour:
                x, y = point[0]
                points.append((float(x), float(y)))

            # 过滤太短的轮廓（噪点）
            if len(points) > 2:
                # 设置填充颜色
                dxfattribs = {'layer': 'OPENCV_OUTLINE', 'closed': True}
                
                # 添加填充
                if fill_color != 'none':
                    if len(points) >= 3:
                        if fill_color == 'black':
                            solid_color = 0
                        else:  # white
                            solid_color = 7
                        
                        # 使用多个SOLID实体填充整个区域
                        # 将多边形分解为多个三角形
                        for i in range(1, len(points) - 1):
                            msp.add_solid(
                                points[0],
                                points[i],
                                points[i+1],
                                points[i+1],
                                dxfattribs={'layer': 'OPENCV_OUTLINE', 'color': solid_color}
                            )
                
                # 添加线条
                msp.add_lwpolyline(points, dxfattribs=dxfattribs)
                total_curves += 1

        print(f"OpenCV found {total_curves} contours.")

        # 清理大内存
        clean_memory(img, gray, binary, in_memory_file)

        # 流式返回 - 使用StringIO
        from io import StringIO
        string_stream = StringIO()
        doc.write(string_stream)
        
        # 转换为BytesIO
        dxf_stream = io.BytesIO()
        dxf_stream.write(string_stream.getvalue().encode('utf-8'))
        dxf_stream.seek(0)

        return send_file(
            dxf_stream,
            as_attachment=True,
            download_name='opencv_vector.dxf',
            mimetype='application/dxf'
        )

    except Exception as e:
        import traceback
        print(f"Conversion Error: {e}")
        traceback.print_exc()
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)