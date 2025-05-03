#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查openpyxl库的所有子模块
用于确保打包时包含所有必要的模块
"""

import os
import sys
import pkgutil
import importlib

def check_module(module_name):
    """检查模块及其所有子模块"""
    print(f"检查模块: {module_name}")
    
    try:
        # 尝试导入模块
        module = importlib.import_module(module_name)
        print(f"成功导入模块: {module_name}")
        
        # 检查模块路径
        if hasattr(module, '__file__'):
            print(f"模块路径: {module.__file__}")
        else:
            print("模块没有文件路径")
        
        # 获取模块的所有子模块
        try:
            # 尝试获取所有子模块
            if hasattr(module, '__path__'):
                print(f"子模块:")
                prefix = module_name + "."
                for finder, name, ispkg in pkgutil.iter_modules(module.__path__, prefix):
                    print(f"  - {name}")
                    
                    # 尝试导入子模块
                    try:
                        sub_module = importlib.import_module(name)
                        if hasattr(sub_module, '__file__'):
                            print(f"    路径: {sub_module.__file__}")
                        else:
                            print(f"    路径: 未知")
                    except ImportError as e:
                        print(f"    导入失败: {e}")
            else:
                print("模块没有子模块")
        except Exception as e:
            print(f"获取子模块失败: {e}")
        
        return True
    except ImportError as e:
        print(f"导入模块失败: {e}")
        return False

def check_specific_module(module_name):
    """检查特定的模块"""
    print(f"\n检查特定模块: {module_name}")
    try:
        module = importlib.import_module(module_name)
        print(f"成功导入模块: {module_name}")
        if hasattr(module, '__file__'):
            print(f"模块路径: {module.__file__}")
        return True
    except ImportError as e:
        print(f"导入模块失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("检查openpyxl库及其子模块")
    print("=" * 50)
    
    # 检查openpyxl主模块
    if check_module('openpyxl'):
        # 检查特定的子模块
        problematic_modules = [
            'openpyxl.cell',
            'openpyxl.cell.cell',
            'openpyxl.cell.text',
            'openpyxl.cell_writer',
            'openpyxl.comments',
            'openpyxl.descriptors',
            'openpyxl.styles',
            'openpyxl.utils',
            'openpyxl.workbook',
            'openpyxl.worksheet'
        ]
        
        for module in problematic_modules:
            check_specific_module(module)
    
    print("\n" + "=" * 50)
    print("检查完成")
    print("=" * 50)

if __name__ == "__main__":
    main() 