"""
CAD图像转换器 - GitHub Actions兼容打包脚本
避免中文文件名和其他兼容性问题
"""

import os
import sys
import subprocess
import shutil

def clean_build_files():
    """清理之前的打包文件"""
    paths_to_remove = ['build', 'dist']
    for path in paths_to_remove:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"已清理目录: {path}")

def build_exe():
    """EXE打包 - 兼容版本"""
    print("开始打包...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'cad_converter',  # 使用英文名避免编码问题
        '--clean',
        '--noconfirm',
        
        # 数据文件
        '--add-data', 'templates;templates',
        
        # 核心模块
        '--hidden-import', 'cv2',
        '--hidden-import', 'numpy',
        '--hidden-import', 'ezdxf',
        '--hidden-import', 'scipy',
        '--hidden-import', 'skimage',
        '--hidden-import', 'PIL',
        '--hidden-import', 'flask',
        '--hidden-import', 'werkzeug',
        '--hidden-import', 'jinja2',
        '--hidden-import', 'markupsafe',
        '--hidden-import', 'itsdangerous',
        '--hidden-import', 'click',
        '--hidden-import', 'blinker',
        '--hidden-import', 'certifi',
        '--hidden-import', 'charset_normalizer',
        '--hidden-import', 'idna',
        '--hidden-import', 'urllib3',
        '--hidden-import', 'imageio',
        '--hidden-import', 'networkx',
        '--hidden-import', 'packaging',
        '--hidden-import', 'pillow',
        '--hidden-import', 'tifffile',
        '--hidden-import', 'lazy_loader',
        '--hidden-import', 'pydoc',
        '--hidden-import', 'pydoc_data',
        
        # 优化选项
        '--optimize', '2',
        
        'main.py'
    ]
    
    try:
        print("执行打包命令...")
        # 使用subprocess.run而不是check=False，避免编码问题
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            exe_path = os.path.join('dist', 'cad_converter.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print("\n打包成功！")
                print(f"可执行文件: {exe_path}")
                print(f"文件大小: {size_mb:.2f} MB")
            else:
                print("\n错误：未找到生成的可执行文件")
        else:
            print(f"\n打包失败，错误码: {result.returncode}")
            if result.stdout:
                print(f"输出: {result.stdout}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
    except Exception as e:
        print(f"\n打包过程中出现异常: {str(e)}")

if __name__ == '__main__':
    if '--clean' in sys.argv:
        clean_build_files()
    build_exe()
