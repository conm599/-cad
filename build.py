"""
CAD图像转换器 - 最终简化打包脚本
只包含必要的功能，避免所有已知问题
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

def build_exe():
    """EXE打包 - 最终简化版本"""
    print("Starting build...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'cad_converter',
        '--clean',
        '--noconfirm',
        '--add-data', 'templates;templates',
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            exe_path = os.path.join('dist', 'cad_converter.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print("Build successful!")
                print(f"Executable: {exe_path}")
                print(f"Size: {size_mb:.2f} MB")
            else:
                print("Error: Executable not found")
        else:
            print(f"Build failed, exit code: {result.returncode}")
    except Exception as e:
        print(f"Exception during build: {str(e)}")

if __name__ == '__main__':
    if '--clean' in sys.argv:
        clean_build_files()
    build_exe()
