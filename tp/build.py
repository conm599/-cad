import os
import sys
import shutil


def build_exe():
    print("=" * 60)
    print("图片转线条图工具 - 打包脚本")
    print("=" * 60)
    print()
    
    print("正在检查依赖...")
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        os.system("pip install pyinstaller")
        print("✓ PyInstaller 安装完成")
    
    print()
    print("开始打包...")
    print()
    
    build_cmd = "pyinstaller --clean ImageToLine.spec"
    
    print(f"执行命令: {build_cmd}")
    print()
    
    result = os.system(build_cmd)
    
    print()
    print("=" * 60)
    if result == 0:
        print("✓ 打包成功！")
        print()
        print("可执行文件位置: dist/ImageToLine.exe")
        print()
        print("你可以:")
        print("  1. 直接运行 dist/ImageToLine.exe")
        print("  2. 将 dist/ImageToLine.exe 复制到其他电脑使用")
    else:
        print("✗ 打包失败，请检查错误信息")
    print("=" * 60)
    
    return result == 0


if __name__ == "__main__":
    build_exe()
