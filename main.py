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

def interpolate_points(points, factor=8):
    """插值增加点数，提高曲线精度"""
    if len(points) < 3:
        print(f"点数太少({len(points)})，不进行插值")
        return points
    
    print(f"开始插值：原始点数={len(points)}，倍数={factor}")
    new_points = []
    
    for i in range(len(points)):
        new_points.append(points[i])
        
        # 在当前点和下一个点之间插入新点
        next_i = (i + 1) % len(points)
        x1, y1 = points[i]
        x2, y2 = points[next_i]
        
        # 插值增加点数 - 确保每个间隔都插入factor-1个点
        for j in range(1, factor):
            t = j / factor
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            new_points.append((x, y))
    
    print(f"插值完成：新点数={len(new_points)}，增加了{len(new_points) - len(points)}个点")
    return new_points

def smooth_curve(points):
    """使用样条曲线平滑轮廓"""
    if len(points) < 3:
        return points
    
    try:
        from scipy import interpolate
        import numpy as np
        
        # 提取x和y坐标
        x_coords = np.array([p[0] for p in points])
        y_coords = np.array([p[1] for p in points])
        
        # 闭合曲线：添加第一个点到末尾
        x_coords = np.append(x_coords, x_coords[0])
        y_coords = np.append(y_coords, y_coords[0])
        
        # 计算参数t
        t = np.arange(len(x_coords))
        
        # 创建样条插值
        tck = interpolate.splrep(t, np.vstack([x_coords, y_coords]).T, s=0, per=True)
        
        # 生成更密集的点
        t_new = np.linspace(0, len(x_coords) - 1, len(x_coords) * 8)
        smooth_points = interpolate.splev(t_new, tck)
        
        # 转换为点列表
        result = [(float(smooth_points[0][i]), float(smooth_points[1][i])) for i in range(len(smooth_points[0]))]
        
        return result
    except ImportError:
        # 如果scipy不可用，使用简单的线性插值
        return interpolate_points(points, factor=8)
    except Exception as e:
        # 如果样条插值失败，使用简单的线性插值
        print(f"平滑曲线失败: {e}")
        return interpolate_points(points, factor=8)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/multi_image')
def multi_image():
    return render_template('multi_image.html')

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

        # 单线条模式处理 - 使用scikit-image的骨架化算法
        if single_line:
            from skimage.morphology import skeletonize
            # 确保二值图像是0和1
            binary_bool = (binary > 0)
            # 使用scikit-image的骨架化算法
            skeleton = skeletonize(binary_bool)
            # 转换回0-255格式
            binary = (skeleton * 255).astype(np.uint8)

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
        high_precision = request.form.get('high_precision', 'none')

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

        # 单线条模式处理 - 使用scikit-image的骨架化算法
        if single_line:
            from skimage.morphology import skeletonize
            # 确保二值图像是0和1
            binary_bool = (binary > 0)
            # 使用scikit-image的骨架化算法
            skeleton = skeletonize(binary_bool)
            # 转换回0-255格式
            binary = (skeleton * 255).astype(np.uint8)

        # 2. 使用 OpenCV 查找轮廓 - 提取所有轮廓
        # 使用RETR_LIST提取所有轮廓（包括内部），避免只识别边框
        
        # 根据高精度模式选择轮廓近似方法
        if high_precision.startswith('more_points_'):
            # 模式1：增加曲线数量 - 保留所有轮廓点
            # 提取倍数
            factor = int(high_precision.split('_')[1])
            print(f"高精度模式：增加曲线数量，倍数={factor}")
            # 使用CHAIN_APPROX_SIMPLE进行轮廓近似，然后插值
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            print(f"轮廓数量：{len(contours)}，使用CHAIN_APPROX_SIMPLE")
        else:
            # 默认模式：使用CHAIN_APPROX_SIMPLE进行轮廓近似，减少重复点
            print(f"高精度模式：{high_precision}")
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            print(f"轮廓数量：{len(contours)}，使用CHAIN_APPROX_SIMPLE")

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

            # 高精度模式处理
            if high_precision.startswith('more_points_') and len(points) > 2:
                # 模式1：增加曲线数量 - 插值增加点数
                # 使用从参数中提取的倍数
                factor = int(high_precision.split('_')[1])
                print(f"原始点数：{len(points)}，倍数：{factor}")
                points = interpolate_points(points, factor=factor)
                print(f"插值后点数：{len(points)}")
            elif high_precision == 'curve_edge' and len(points) > 2:
                # 模式2：曲线边缘 - 使用样条曲线
                print(f"原始点数：{len(points)}，使用曲线边缘")
                points = smooth_curve(points)
                print(f"平滑后点数：{len(points)}")

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
