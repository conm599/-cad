from PIL import Image, ImageDraw, ImageFont
import os


def create_icon():
    icon_size = 256
    img = Image.new('RGBA', (icon_size, icon_size), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)
    
    center_x = icon_size // 2
    center_y = icon_size // 2
    
    draw.rectangle([40, 40, icon_size - 40, icon_size - 40], 
                   outline=(0, 150, 255, 255), width=8)
    
    for i in range(3):
        y = 80 + i * 50
        draw.line([60, y, icon_size - 60, y], 
                  fill=(255, 255, 255, 255), width=6)
    
    draw.line([center_x, 60, center_x, icon_size - 60], 
              fill=(0, 150, 255, 255), width=8)
    
    draw.line([60, center_y, icon_size - 60, center_y], 
              fill=(0, 150, 255, 255), width=8)
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        ico_images.append(resized)
    
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    ico_images[0].save(icon_path, format='ICO', sizes=[(size[0], size[1]) for size in sizes])
    
    print(f"✓ 图标已创建: {icon_path}")
    return icon_path


if __name__ == "__main__":
    create_icon()
