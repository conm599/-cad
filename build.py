"""
CAD图像转换器 - 完整打包脚本
包含所有必要的模块，避免运行时错误
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

def build_full_exe():
    """完整打包，包含所有模块"""
    print("开始完整打包...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'CAD转换器',
        '--clean',
        '--noconfirm',
        
        # 数据文件
        '--add-data', 'templates;templates',
        
        # 核心Python模块
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
        '--hidden-import', 'requests',
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
    
    print(f"执行打包命令...")
    result = subprocess.run(cmd, check=False)
    
    if result.returncode == 0:
        exe_path = os.path.join('dist', 'CAD转换器.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n打包成功！")
            print(f"可执行文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
    else:
        print(f"打包失败，错误码: {result.returncode}")

if __name__ == '__main__':
    if '--clean' in sys.argv:
        clean_build_files()
    build_full_exe()
