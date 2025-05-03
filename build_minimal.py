#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最小版本的批量文件处理工具打包脚本
使用onefile模式生成单文件可执行程序，体积小、启动快，不显示控制台窗口
"""

import os
import sys
import subprocess
import platform
import time
import shutil
import glob

# 增加递归限制
sys.setrecursionlimit(sys.getrecursionlimit() * 5)
print(f"递归限制已增加到: {sys.getrecursionlimit()}")

def find_tkdnd_files():
    """查找系统中的tkdnd库文件"""
    try:
        # 尝试导入tkinterdnd2来找到其路径
        import tkinterdnd2
        tkdnd_dir = os.path.dirname(tkinterdnd2.__file__)
        print(f"找到tkinterdnd2库路径: {tkdnd_dir}")
        
        # 检查tkdnd目录是否存在
        tkdnd_path = os.path.join(tkdnd_dir, 'tkdnd')
        if os.path.exists(tkdnd_path):
            print(f"找到tkdnd目录: {tkdnd_path}")
            return tkdnd_path
        else:
            print(f"未找到tkdnd目录")
            return None
    except ImportError:
        print("未安装tkinterdnd2库")
        return None

def main():
    # 清理旧的打包文件
    if os.path.exists('dist'):
        print("清理旧的输出目录...")
        try:
            shutil.rmtree('dist')
        except:
            print("清理目录失败，继续执行...")
    
    # 创建输出目录
    os.makedirs('dist', exist_ok=True)
    
    # 确定资源文件的分隔符（Windows用分号，其他平台用冒号）
    separator = ';' if platform.system() == 'Windows' else ':'
    
    # 查找tkdnd库文件并准备添加到打包中
    tkdnd_path = find_tkdnd_files()
    add_data_args = [f'--add-data=resources{separator}resources']
    
    if tkdnd_path:
        # 将tkdnd库添加到打包中
        tkdnd_data_arg = f'--add-data={tkdnd_path}{separator}tkinterdnd2/tkdnd'
        add_data_args.append(tkdnd_data_arg)
        print(f"将添加tkdnd库到打包: {tkdnd_data_arg}")
    
    # 构建打包命令 - 优化版本，改进启动速度
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',  # 使用单文件模式
    ]
    
    # 添加资源文件
    cmd.extend(add_data_args)
    
    # 添加其他参数
    cmd.extend([
        '--hidden-import=openpyxl.cell._writer',
        # 排除更多不必要的模块，减小体积并提高启动速度
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=PIL._tkinter_finder',
        '--exclude-module=docutils',
        '--exclude-module=sphinx',
        '--exclude-module=jedi',
        '--exclude-module=IPython',
        '--exclude-module=pygments',
        '--exclude-module=setuptools',
        '--exclude-module=cryptography',
        '--exclude-module=pyarrow',
        '--exclude-module=pygame',
        '--exclude-module=pytest',
        '--exclude-module=nose',
        '--exclude-module=flask',
        '--exclude-module=notebook',
        '--exclude-module=sqlalchemy',
        '--exclude-module=PySide2',
        '--exclude-module=PyQt5',
        '--exclude-module=PyQt6',
        '--exclude-module=wx',
        '--exclude-module=email_validator',
        '--exclude-module=jupyter',
        '--exclude-module=spyder',
        '--exclude-module=nbconvert',
        '--exclude-module=nbformat',
        '--exclude-module=Cython',
        '--exclude-module=statsmodels',
        '--exclude-module=skimage',
        '--exclude-module=sklearn',
        '--exclude-module=h5py',
        '--exclude-module=tables',
        '--exclude-module=PyInstaller',
        '--exclude-module=pip',
        '--exclude-module=wheel',
        '--upx-dir=upx',  # 使用UPX压缩可执行文件（如果有）
        '--windowed',  # 使用窗口模式，不显示控制台
        '--icon=resources/icons/logo.ico',  # 设置图标
        '--name=批量文件处理工具',  # 直接设置输出文件名
        '--distpath=dist',  # 直接输出到dist目录
        'main.py'
    ])
    
    # 尝试下载UPX（如果不存在）
    if not os.path.exists('upx'):
        try:
            print("正在下载UPX压缩工具以减小输出文件大小...")
            # 为Windows下载UPX
            import urllib.request
            import zipfile
            
            os.makedirs('upx', exist_ok=True)
            urllib.request.urlretrieve(
                "https://github.com/upx/upx/releases/download/v4.2.2/upx-4.2.2-win64.zip",
                "upx.zip"
            )
            
            with zipfile.ZipFile("upx.zip", 'r') as zip_ref:
                zip_ref.extractall("upx_temp")
            
            # 移动upx.exe到upx目录
            upx_exe = glob.glob("upx_temp/*/upx.exe")[0]
            shutil.copy2(upx_exe, "upx/upx.exe")
            
            # 清理临时文件
            shutil.rmtree("upx_temp")
            os.remove("upx.zip")
            
            print("UPX下载完成")
        except Exception as e:
            print(f"下载UPX失败: {e}")
            # 移除UPX选项
            cmd.remove('--upx-dir=upx')
    
    # 执行命令
    print("开始打包...")
    print("命令:", ' '.join(cmd))
    
    start_time = time.time()
    
    try:
        # 实时显示输出
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 实时打印输出
        for line in process.stdout:
            print(line, end='')
        
        # 等待进程完成
        process.wait()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if process.returncode == 0:
            print(f"\n打包成功! 用时: {elapsed_time:.2f}秒")
            
            # 输出文件路径
            output_file = os.path.join('dist', '批量文件处理工具.exe')
            
            if os.path.exists(output_file):
                file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"生成的可执行文件: {output_file}")
                print(f"文件大小: {file_size_mb:.2f} MB")
                print("双击文件即可直接启动，不会显示控制台窗口")
            else:
                print(f"找不到输出文件: {output_file}")
        else:
            print("\n打包失败!")
    except Exception as e:
        print(f"执行失败: {e}")

if __name__ == "__main__":
    main() 