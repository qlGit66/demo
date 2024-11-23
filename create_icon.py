from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # 创建icons目录
    if not os.path.exists('icons'):
        os.makedirs('icons')

    # 创建一个新的图像，大小为48x48像素
    size = 48
    image = Image.new('RGBA', (size, size), (76, 175, 80, 255))  # 使用绿色背景
    draw = ImageDraw.Draw(image)

    # 添加文字
    try:
        # 尝试加载中文字体
        font = ImageFont.truetype("simhei.ttf", 24)  # Windows下的黑体
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", 24)  # 如果没有中文字体，使用Arial
        except:
            font = ImageFont.load_default()  # 如果都没有，使用默认字体

    # 在图像中心绘制文字
    text = "答"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # 绘制白色文字
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # 保存图标
    icon_path = 'icon48.png'
    image.save(icon_path, 'PNG')
    print(f'图标已创建: {icon_path}')

if __name__ == '__main__':
    create_icon() 