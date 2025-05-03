#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量文件处理工具打包脚本
用于将Python应用打包为独立可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_required_modules():
    """分析项目，找出必要的模块"""
    print("分析项目依赖...")
    
    # 核心依赖
    required_modules = [
        "tkinter",      # GUI主框架
        "os",           # 文件操作
        "sys",          # 系统操作
        "logging",      # 日志系统
        "datetime",     # 日期时间处理
        "re",           # 正则表达式
        "webbrowser",   # 打开网页
        "openpyxl",     # Excel文件处理
        "shutil",       # 文件操作增强
        "PIL",          # 图像处理
        "tkinterdnd2",  # 拖放支持
    ]
    
    # 额外数据文件
    datas = [
        # 添加项目中的必要文件
        ('resources', 'resources'),  # 添加资源文件夹
    ]
    
    return required_modules, datas

def create_spec_file(app_name, dist_dir="dist_new"):
    """创建自定义spec文件"""
    print("创建spec文件...")
    
    modules, datas = find_required_modules()
    hidden_imports = ', '.join([f"'{m}'" for m in modules])
    data_items = ', '.join([f"('{src}', '{dst}')" for src, dst in datas])
    
    # 规范化版本信息
    version = '1.0.0'
    
    # 检查图标文件是否存在
    icon_path = os.path.join('resources', 'icons', 'logo.ico')
    icon_path = icon_path.replace('\\', '/')  # 修复反斜杠问题
    if os.path.exists(icon_path):
        print(f"找到图标文件: {icon_path}")
        icon_setting = f"icon='{icon_path}',"
    else:
        print(f"警告: 图标文件不存在: {icon_path}, 将使用默认图标")
        icon_setting = ""
    
    # 确保输出目录存在
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 添加对openpyxl的特殊处理
openpyxl_datas = []
openpyxl_hiddenimports = []

try:
    import openpyxl
    import os
    import pkgutil
    
    # 添加所有openpyxl子模块
    base_package = 'openpyxl'
    imported_pkg = __import__(base_package)
    
    # 递归获取所有子模块
    for importer, modname, ispkg in pkgutil.walk_packages(
        imported_pkg.__path__, prefix=imported_pkg.__name__ + '.'):
        openpyxl_hiddenimports.append(modname)
    
    # 添加openpyxl数据文件
    base_dir = os.path.dirname(openpyxl.__file__)
    if os.path.exists(base_dir):
        # 确保包含openpyxl的所有数据文件
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.xml') or file.endswith('.rel'):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join('openpyxl', os.path.relpath(src_file, base_dir))
                    openpyxl_datas.append((src_file, os.path.dirname(dst_file)))
except ImportError:
    pass

print("添加openpyxl子模块:", openpyxl_hiddenimports)
print("添加openpyxl数据文件:", len(openpyxl_datas))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[{data_items}] + openpyxl_datas,
    hiddenimports=[{hidden_imports}] + openpyxl_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
              'IPython', 'tornado', 'notebook', 'jedi', 'pyarrow', 'cryptography',
              'numba', 'cvxpy', 'sphinx', 'pytest', 'unittest', 'docx', 'pptx', 'setuptools',
              'wheel', 'pip', 'pygments', 'watchdog'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 开启控制台，方便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_setting}
    version='file_version_info.txt',
    distpath=r'{dist_dir}',
)
"""
    
    # 创建版本信息文件
    with open('file_version_info.txt', 'w', encoding='utf-8') as f:
        f.write(f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version.replace('.', ', ')}, 0),
    prodvers=({version.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404b0',
        [StringStruct(u'CompanyName', u'ETF迷你小富胖子'),
        StringStruct(u'FileDescription', u'批量文件处理工具'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2025 ETF迷你小富胖子'),
        StringStruct(u'ProductName', u'批量文件处理工具'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)""")
    
    # 保存spec文件
    with open(f'{app_name}.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return f'{app_name}.spec'

def build_executable(app_name, dist_dir="dist_new"):
    """构建可执行文件"""
    print(f"开始构建 {app_name}...")
    
    # 创建spec文件
    spec_file = create_spec_file(app_name, dist_dir)
    
    # 执行PyInstaller构建命令
    try:
        # 尝试使用python -m pyinstaller来运行
        cmd = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean',          # 清理临时文件
            '--noconfirm',      # 不要询问确认
            spec_file           # 使用我们的自定义spec文件
        ]
        
        print("执行构建命令:", ' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("构建失败:")
            print(result.stderr)
            return False
        
        print(f"构建成功! 可执行文件位于 {dist_dir}/{app_name}.exe")
        
        # 成功后复制到dist目录
        try:
            if not os.path.exists('dist'):
                os.makedirs('dist')
            
            src_file = os.path.join(dist_dir, f"{app_name}.exe")
            dst_file = os.path.join('dist', f"{app_name}.exe")
            
            if os.path.exists(src_file):
                # 如果目标文件已存在，尝试删除
                if os.path.exists(dst_file):
                    try:
                        os.remove(dst_file)
                    except:
                        print(f"无法删除已有文件: {dst_file}")
                        return True
                
                # 复制文件
                shutil.copy2(src_file, dst_file)
                print(f"已将可执行文件复制到 dist/{app_name}.exe")
            else:
                print(f"源文件不存在: {src_file}")
        except Exception as e:
            print(f"复制文件失败: {e}")
        
        return True
    except Exception as e:
        print(f"执行构建命令失败: {e}")
        print("尝试备用方式...")
        
        # 备用方式：直接调用pyinstaller模块
        try:
            import PyInstaller.__main__
            
            print("使用PyInstaller.__main__模块直接构建")
            PyInstaller.__main__.run([
                '--clean',
                '--noconfirm',
                spec_file
            ])
            
            print(f"构建完成! 可执行文件位于 {dist_dir}/{app_name}.exe")
            return True
        except Exception as e2:
            print(f"备用构建方式也失败了: {e2}")
            return False

def cleanup():
    """清理临时文件"""
    print("清理临时文件...")
    
    # 删除spec文件和版本信息文件
    for file in ['file_version_info.txt', '*.spec']:
        try:
            for f in Path('.').glob(file):
                f.unlink()
        except Exception as e:
            print(f"删除 {file} 失败: {e}")
    
    # 保留dist目录，但删除build目录
    try:
        if os.path.exists('build'):
            shutil.rmtree('build')
    except Exception as e:
        print(f"删除build目录失败: {e}")

def main():
    """主函数"""
    app_name = "批量文件处理工具"
    dist_dir = "dist_new"
    
    print("=" * 50)
    print(f"开始打包 {app_name}")
    print("=" * 50)
    
    # 构建可执行文件
    success = build_executable(app_name, dist_dir)
    
    # 清理临时文件
    cleanup()
    
    if success:
        print("\n" + "=" * 50)
        print(f"{app_name} 打包成功!")
        print(f"可执行文件位于: {dist_dir}/{app_name}.exe")
        if os.path.exists(os.path.join('dist', f"{app_name}.exe")):
            print(f"同时也复制到了: dist/{app_name}.exe")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("打包失败，请检查错误信息。")
        print("=" * 50)

if __name__ == "__main__":
    main() 