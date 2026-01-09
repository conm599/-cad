# CAD图像转换器

一个基于Python的图像转DXF工具，支持多种图像处理功能和自定义选项。

## 功能特性
- **阈值调整**：自定义图像二值化阈值
- **反色功能**：支持黑色背景处理
- **单线条模式**：减小线条之间的缝隙，优化显示效果
- **忽略边缘**：添加白色边框，分离主体内容和图像边框
- **实时预览**：处理前查看效果
- **DXF导出**：生成兼容CAD软件的DXF文件

## 安装方法

### 方法二：从源码运行
1. 克隆仓库：
   ```bash
   git clone <仓库地址>
   cd cad
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 启动程序：
   ```bash
   python main.py
   ```

5. 在浏览器中访问`http://127.0.0.1:5000`

## 使用说明

1. **上传图片**：点击"加载图片"按钮选择图片文件
2. **调整参数**：
   - 阈值：控制图像二值化的灵敏度
   - 反色：切换黑色/白色背景
   - 忽略边缘：添加白色边框
3. **预览效果**：点击"更新预览"查看处理效果
4. **导出DXF**：点击"导出DXF"下载文件

## 技术栈

- **Python 3.14**：开发语言
- **Flask**：Web框架
- **OpenCV**：图像处理
- **NumPy**：数值计算
- **ezdxf**：DXF文件生成
- **PyInstaller**：EXE打包

## 项目结构

```
cad/
├── main.py              # 主程序文件
├── templates/
│   └── index.html       # 前端页面
├── requirements.txt     # 依赖列表
├── venv/               # 虚拟环境（可选）
├     
└── README.md           # 项目说明
```

## 许可证

MIT License

## 注意事项

- 支持的图像格式：JPG、PNG、BMP等
- 推荐使用分辨率适中的图片
- 单线条模式适合简单图形处理
- 忽略边缘功能有助于在CAD中编辑图像

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的图像转DXF功能
- 实现忽略边缘功能
