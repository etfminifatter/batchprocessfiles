#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建应用图标
将PNG图像转换为ICO格式，用于应用程序图标
"""

import os
from PIL import Image

def create_icon_from_png(png_file, ico_file, sizes=None):
    """
    将PNG图像转换为ICO格式
    
    Args:
        png_file (str): PNG图像文件路径
        ico_file (str): 输出的ICO文件路径
        sizes (list): 图标尺寸列表，默认为[16, 32, 48, 64, 128, 256]
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]
    
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(ico_file), exist_ok=True)
        
        # 打开PNG图像
        img = Image.open(png_file)
        
        # 创建不同尺寸的图像
        icon_images = []
        for size in sizes:
            # 调整图像大小
            resized_img = img.resize((size, size), Image.LANCZOS)
            icon_images.append(resized_img)
        
        # 保存为ICO文件
        icon_images[0].save(
            ico_file,
            format='ICO',
            sizes=[(img.width, img.height) for img in icon_images],
            append_images=icon_images[1:]
        )
        
        print(f"成功创建图标: {ico_file}")
        return True
    except Exception as e:
        print(f"创建图标失败: {e}")
        return False

def main():
    """主函数"""
    # 源图像文件
    source_png = os.path.join("source_img", "批量创建功能.png")
    
    # 输出ICO文件
    icon_file = os.path.join("resources", "icons", "logo.ico")
    
    # 创建图标
    if os.path.exists(source_png):
        success = create_icon_from_png(source_png, icon_file)
        if success:
            print("图标创建成功!")
        else:
            print("图标创建失败.")
    else:
        print(f"源图像文件不存在: {source_png}")
        print("请提供有效的PNG图像文件.")

if __name__ == "__main__":
    main() 