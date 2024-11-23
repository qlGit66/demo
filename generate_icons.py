from PIL import Image
import os

def create_icons_from_image(source_image_path):
    # 创建 icons 目录
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # 图标尺寸
    sizes = [48]  # 我们只需要48x48的图标
    
    # 打开源图片
    with Image.open(source_image_path) as img:
        # 确保图片是 RGBA 模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        for size in sizes:
            # 创建一个新的图像副本
            resized_image = img.copy()
            # 使用 Resampling.LANCZOS 替代 ANTIALIAS
            resized_image.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # 保存图标
            icon_path = os.path.join('icons', f'icon{size}.png')
            resized_image.save(icon_path, 'PNG')
            print(f'Created icon: {icon_path}')

if __name__ == '__main__':
    # 源图片路径
    source_image_path = 'cat.jpg'  # 确保这个路径指向你的猫咪图片
    
    if not os.path.exists(source_image_path):
        print(f'Error: Source image not found at {source_image_path}')
        exit(1)
        
    create_icons_from_image(source_image_path)
    print('Icon generation complete!') 