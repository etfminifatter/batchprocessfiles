import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import logging
import os
import sys

# 导入各个标签页
from ui.tabs.create_files_tab import CreateFilesTab
from ui.tabs.create_dirs_tab import CreateDirsTab
from ui.tabs.create_sheets_tab import CreateSheetsTab
from ui.tabs.rename_tab import RenameTab
from ui.tabs.move_copy_tab import MoveCopyTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger('main_window')
        self.logger.info("主窗口初始化")
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 设置主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置UI结构
        self.setup_menu()
        self.setup_notebook()
        self.setup_status_bar()
        self.setup_bottom_buttons()
        
        self.logger.info("用户界面设置完成")
        
    def setup_menu(self):
        """设置菜单栏"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 将官网、赞赏等放在顶级菜单
        self.menu_bar.add_command(label="官网", command=self.open_website)
        self.menu_bar.add_command(label="赞赏", command=self.show_donation)
        self.menu_bar.add_command(label="广告", command=self.show_ads)
        self.menu_bar.add_command(label="帮助", command=self.show_help)
        self.menu_bar.add_command(label="关于", command=self.show_about)
        
        self.logger.info("菜单栏设置完成")
        
    def setup_notebook(self):
        """设置标签页"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页
        self.create_files_tab = CreateFilesTab(self.notebook)
        self.create_dirs_tab = CreateDirsTab(self.notebook)
        self.create_sheets_tab = CreateSheetsTab(self.notebook)
        self.rename_tab = RenameTab(self.notebook)
        self.move_copy_tab = MoveCopyTab(self.notebook)
        
        # 添加标签页到Notebook
        self.notebook.add(self.create_files_tab, text="创建文件")
        self.notebook.add(self.create_dirs_tab, text="创建目录")
        self.notebook.add(self.create_sheets_tab, text="创建工作表")
        self.notebook.add(self.rename_tab, text="重命名")
        self.notebook.add(self.move_copy_tab, text="移动/复制")
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.logger.info("标签页设置完成")
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = ttk.Frame(self.main_frame, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态信息
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(self.status_bar, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        # 版本信息
        version = "1.0.0"
        ttk.Label(self.status_bar, text=f"版本: {version}").pack(side=tk.RIGHT, padx=5)
        
        self.logger.info("状态栏设置完成")
    
    def setup_bottom_buttons(self):
        """设置底部按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # 为了更好的视觉效果，添加一个分隔线
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
        
        # 执行按钮（按照惯例，执行按钮放在右侧）
        execute_button = ttk.Button(
            button_frame, 
            text="执行", 
            style="Primary.TButton",
            command=self.execute_action,
            width=15
        )
        execute_button.pack(side=tk.RIGHT, padx=10)
        
        # 预览按钮
        preview_button = ttk.Button(
            button_frame, 
            text="预览", 
            style="Secondary.TButton",
            command=self.preview_action,
            width=15
        )
        preview_button.pack(side=tk.RIGHT, padx=10)
        
        self.logger.info("底部按钮设置完成")
        
    def on_tab_changed(self, event):
        """标签页切换事件"""
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text")
        self.logger.info(f"切换到标签页: {tab_text}")
        self.status_var.set(f"当前: {tab_text}")
    
    def preview_action(self):
        """执行预览操作"""
        current_tab_id = self.notebook.select()
        current_tab = self.notebook.nametowidget(current_tab_id)
        
        self.logger.info(f"执行预览操作: {type(current_tab).__name__}")
        
        try:
            if hasattr(current_tab, 'preview'):
                current_tab.preview()
            else:
                self.logger.warning(f"当前标签页没有预览功能")
                messagebox.showwarning("提示", "当前功能不支持预览")
        except Exception as e:
            self.logger.error(f"预览操作失败: {str(e)}")
            messagebox.showerror("错误", f"预览操作失败: {str(e)}")
    
    def execute_action(self):
        """执行操作"""
        current_tab_id = self.notebook.select()
        current_tab = self.notebook.nametowidget(current_tab_id)
        
        self.logger.info(f"执行操作: {type(current_tab).__name__}")
        
        try:
            if hasattr(current_tab, 'execute'):
                current_tab.execute()
            else:
                self.logger.warning(f"当前标签页没有执行功能")
                messagebox.showwarning("提示", "当前功能不支持执行")
        except Exception as e:
            self.logger.error(f"执行操作失败: {str(e)}")
            messagebox.showerror("错误", f"执行操作失败: {str(e)}")
            
    def open_website(self):
        """打开官方网站"""
        self.logger.info("打开官方网站")
        url = "https://www.example.com/batch-file-tool"
        try:
            webbrowser.open(url)
        except Exception as e:
            self.logger.error(f"打开网站失败: {str(e)}")
            messagebox.showerror("错误", f"打开网站失败: {str(e)}")
    
    def show_donation(self):
        """显示赞助信息"""
        self.logger.info("显示赞助信息")
        donation_info = """
        感谢您使用批量文件处理工具！
        
        如果您觉得这个工具对您有帮助，可以考虑支持我们的开发：
        
        支付宝：example@example.com
        微信：example_wechat
        
        您的支持是我们持续改进的动力！
        """
        messagebox.showinfo("赞助", donation_info)
    
    def show_ads(self):
        """显示广告信息"""
        self.logger.info("显示广告信息")
        ads_info = """
        推荐产品：高级批处理工具套件
        
        - 支持更多文件格式
        - 提供更多自定义选项
        - 包含高级批量图像处理功能
        - 支持脚本自动化
        
        详情请访问：https://www.example.com/advanced-tools
        """
        messagebox.showinfo("产品推荐", ads_info)
    
    def show_help(self):
        """显示帮助信息"""
        self.logger.info("显示帮助信息")
        help_info = """
        批量文件处理工具使用指南：
        
        1. 创建文件：批量创建空文件或带模板内容的文件
        2. 创建目录：批量创建目录结构，支持层级
        3. 创建工作表：批量创建Excel工作表
        4. 重命名：批量重命名文件，支持替换、添加前后缀等
        5. 移动/复制：批量移动或复制文件
        
        详细使用说明请访问官方网站。
        """
        messagebox.showinfo("帮助", help_info)
    
    def show_about(self):
        """显示关于信息"""
        self.logger.info("显示关于信息")
        about_info = """
        批量文件处理工具 v1.0.0
        
        一个简单易用的批量文件处理工具，帮助您提高工作效率。
        
        版权所有 © 2023
        作者：示例开发者
        """
        messagebox.showinfo("关于", about_info) 