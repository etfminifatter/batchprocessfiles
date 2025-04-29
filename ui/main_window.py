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
        
        # 检查关键样式是否存在
        style = ttk.Style()
        styles = ['Primary.TButton', 'Secondary.TButton', 'TabSelected.TButton']
        for style_name in styles:
            try:
                # 尝试获取样式的背景色，如果样式不存在会抛出异常
                bg = style.lookup(style_name, 'background')
                self.logger.info(f"样式 {style_name} 已加载，背景色: {bg}")
            except Exception as e:
                self.logger.error(f"样式 {style_name} 未正确加载: {str(e)}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 设置主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置UI结构，调整初始化顺序
        self.setup_menu()
        self.setup_nav_buttons()
        self.setup_status_bar()  # 先初始化状态栏，确保status_var可用
        self.setup_content_area()  # 再初始化内容区
        
        # 验证UI组件是否正确创建
        self.validate_ui_components()
        
        self.logger.info("用户界面设置完成")
        
    def validate_ui_components(self):
        """验证所有UI组件是否正确创建"""
        # 检查重要组件是否存在
        components = {
            "主框架": hasattr(self, "main_frame"),
            "导航按钮": hasattr(self, "nav_buttons") and len(self.nav_buttons) > 0,
            "标签页": hasattr(self, "tabs") and len(self.tabs) > 0,
            "状态栏": hasattr(self, "status_bar"),
            "状态变量": hasattr(self, "status_var"),
            "内容区": hasattr(self, "content_frame")
        }
        
        for name, exists in components.items():
            if exists:
                self.logger.info(f"组件 {name} 已成功创建")
            else:
                self.logger.error(f"组件 {name} 可能未正确创建")
        
        # 确保底部按钮可见
        try:
            # 查找所有子窗口部件
            all_children = self.main_frame.winfo_children()
            # 记录各类型窗口部件的数量
            widget_counts = {}
            for child in all_children:
                widget_type = child.winfo_class()
                if widget_type not in widget_counts:
                    widget_counts[widget_type] = 0
                widget_counts[widget_type] += 1
            
            self.logger.info(f"主窗口包含以下窗口部件: {widget_counts}")
            
            # 特别检查按钮
            buttons = [w for w in all_children if w.winfo_class() == "TButton"]
            if buttons:
                self.logger.info(f"找到 {len(buttons)} 个按钮")
                for btn in buttons:
                    self.logger.debug(f"按钮: {btn.cget('text')}")
            else:
                self.logger.warning("未找到任何按钮")
        except Exception as e:
            self.logger.error(f"验证UI组件失败: {str(e)}")
    
    def setup_menu(self):
        """设置导航栏（顶部菜单）"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 顶级菜单项
        self.menu_bar.add_command(label="官网", command=self.open_website)
        self.menu_bar.add_command(label="赞赏", command=self.show_donation)
        self.menu_bar.add_command(label="广告", command=self.show_ads)
        self.menu_bar.add_command(label="帮助", command=self.show_help)
        self.menu_bar.add_command(label="关于", command=self.show_about)
        
        self.logger.info("导航栏设置完成")
    
    def setup_nav_buttons(self):
        """设置功能选项卡（水平按钮组）"""
        # 创建一个带背景色的框架用于放置按钮，增强视觉层次感
        nav_container = ttk.Frame(self.main_frame)
        nav_container.pack(fill=tk.X, pady=(5, 10))
        
        # 创建一个内部框架用于放置按钮
        self.nav_frame = ttk.Frame(nav_container)
        self.nav_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 定义功能按钮
        self.nav_buttons = []
        nav_options = [
            {"text": "创建文件", "command": lambda: self.switch_tab(0)},
            {"text": "创建目录", "command": lambda: self.switch_tab(1)},
            {"text": "创建工作表", "command": lambda: self.switch_tab(2)},
            {"text": "重命名", "command": lambda: self.switch_tab(3)},
            {"text": "移动/复制", "command": lambda: self.switch_tab(4)}
        ]
        
        # 创建按钮
        for i, opt in enumerate(nav_options):
            btn = ttk.Button(
                self.nav_frame,
                text=opt["text"],
                command=opt["command"],
                style="Tab.TButton",
                width=12
            )
            btn.pack(side=tk.LEFT, padx=3)  # 增加按钮间距
            
            # 添加鼠标悬停效果的绑定
            btn.bind("<Enter>", lambda e, b=btn: self._on_tab_hover(e, b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_tab_hover(e, b, False))
            
            self.nav_buttons.append(btn)
        
        # 添加底部分隔线，增强视觉区分
        separator = ttk.Separator(nav_container, orient='horizontal')
        separator.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        # 初始化当前选中的标签页
        self.current_tab_index = 0
        self.mark_selected_button()
        
        self.logger.info("功能选项卡设置完成")
    
    def _on_tab_hover(self, event, button, is_enter):
        """处理标签页按钮的鼠标悬停事件"""
        # 只有未选中的按钮才改变样式
        btn_index = self.nav_buttons.index(button)
        if btn_index != self.current_tab_index:
            # 突出显示当前悬停的按钮，但不要改变已选中的按钮
            if is_enter:
                # 鼠标进入，添加悬停效果
                button.state(['active'])
            else:
                # 鼠标离开，移除悬停效果
                button.state(['!active'])
    
    def setup_content_area(self):
        """设置主内容区"""
        # 创建主内容框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))  # 顶部和侧面有内边距，底部无内边距
        
        # 创建一个框架来容纳所有标签页内容
        self.tab_contents = ttk.Frame(self.content_frame)
        self.tab_contents.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页，但初始不显示
        self.tabs = [
            CreateFilesTab(self.tab_contents),
            CreateDirsTab(self.tab_contents),
            CreateSheetsTab(self.tab_contents),
            RenameTab(self.tab_contents),
            MoveCopyTab(self.tab_contents)
        ]
        
        # 设置底部按钮区域，独立放在main_frame中，在状态栏之上
        self.setup_bottom_buttons()
        
        # 显示第一个标签页
        self.switch_tab(0)
        
        self.logger.info("主内容区设置完成")
    
    def switch_tab(self, index):
        """切换标签页"""
        # 如果点击当前已选中的标签页，不做任何操作
        if self.current_tab_index == index:
            return
        
        # 隐藏当前显示的标签页
        self.tabs[self.current_tab_index].pack_forget()
        
        # 添加简单的视觉反馈 - 按钮短暂进入pressed状态
        self.nav_buttons[index].state(['pressed'])
        self.root.update_idletasks()  # 强制更新UI
        self.root.after(100)  # 短暂延迟，产生视觉反馈
        self.nav_buttons[index].state(['!pressed'])
        
        # 显示新选择的标签页
        self.tabs[index].pack(fill=tk.BOTH, expand=True)
        
        # 更新当前标签页索引
        self.current_tab_index = index
        
        # 更新按钮样式
        self.mark_selected_button()
        
        # 更新状态栏
        tab_names = ["创建文件", "创建目录", "创建工作表", "重命名", "移动/复制"]
        self.status_var.set(f"当前: {tab_names[index]}")
        
        self.logger.info(f"切换到标签页: {tab_names[index]}")
    
    def mark_selected_button(self):
        """标记选中的按钮"""
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_tab_index:
                btn.configure(style="TabSelected.TButton")
            else:
                btn.configure(style="Tab.TButton")
        
    def setup_bottom_buttons(self):
        """设置底部按钮区域"""
        # 创建底部按钮框架 - 使用ActionBar样式，放在状态栏之上
        button_frame = ttk.Frame(self.main_frame, style="ActionBar.TFrame")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(8, 5), before=self.status_bar)
        
        # 按钮内容区域，添加内边距提升层次感
        button_content = ttk.Frame(button_frame, style="ActionBar.TFrame")
        button_content.pack(fill=tk.X, padx=5, pady=8)
        
        # 为了更好的视觉效果，添加一个分隔线
        separator = ttk.Separator(button_frame, orient='horizontal')
        separator.pack(side=tk.TOP, fill=tk.X)
        
        # 执行按钮（按照惯例，执行按钮放在右侧）- 改为辅助按钮样式
        execute_button = ttk.Button(
            button_content, 
            text="执行", 
            style="Auxiliary.TButton",
            command=self.execute_action,
            width=12
        )
        execute_button.pack(side=tk.RIGHT, padx=5)
        
        # 预览按钮 - 改为辅助按钮样式
        preview_button = ttk.Button(
            button_content, 
            text="预览", 
            style="Auxiliary.TButton",
            command=self.preview_action,
            width=12
        )
        preview_button.pack(side=tk.RIGHT, padx=5)
        
        self.logger.info("底部按钮设置完成")
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = ttk.Frame(self.main_frame, relief=tk.GROOVE, borderwidth=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态信息
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        # 添加状态图标（圆点）
        status_frame = ttk.Frame(self.status_bar)
        status_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 创建状态指示器画布 - 使用系统默认背景色
        status_indicator = tk.Canvas(status_frame, width=10, height=10, 
                                   bg="#F0F0F0",  # 使用固定的背景色代替cget
                                   highlightthickness=0)
        status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        # 画一个绿色圆点表示系统正常
        status_indicator.create_oval(2, 2, 8, 8, fill="#4CAF50", outline="")
        
        # 状态文本
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 9))
        status_label.pack(side=tk.LEFT)
        
        # 版本信息，使用更细的字体
        version = "1.0.0"
        version_frame = ttk.Frame(self.status_bar)
        version_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        ttk.Label(version_frame, text=f"版本: {version}", 
                 font=('Arial', 8), foreground='#616161').pack(side=tk.RIGHT)
        
        self.logger.info("状态栏设置完成")
    
    def preview_action(self):
        """执行预览操作"""
        current_tab = self.tabs[self.current_tab_index]
        
        self.logger.info(f"执行预览操作: {type(current_tab).__name__}")
        
        # 添加按钮按下的视觉反馈
        preview_button = None
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_class() == "TFrame":
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == "预览":
                                preview_button = btn
                                break
        
        if preview_button:
            preview_button.state(['pressed'])
            self.root.update_idletasks()
            self.root.after(150)
            preview_button.state(['!pressed'])
        
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
        current_tab = self.tabs[self.current_tab_index]
        
        self.logger.info(f"执行操作: {type(current_tab).__name__}")
        
        # 添加按钮按下的视觉反馈
        execute_button = None
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_class() == "TFrame":
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == "执行":
                                execute_button = btn
                                break
        
        if execute_button:
            execute_button.state(['pressed'])
            self.root.update_idletasks()
            self.root.after(150)  # 稍长一点的延迟，增强反馈效果
            execute_button.state(['!pressed'])
        
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