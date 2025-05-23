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
    def __init__(self, root, dnd_available=True):
        self.root = root
        self.logger = logging.getLogger('main_window')
        self.logger.info("主窗口初始化")
        # 保存拖放功能可用性状态
        self.dnd_available = dnd_available
        self.logger.info(f"拖放功能状态: {'可用' if dnd_available else '不可用'}")
        
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
        # 设置主框架，应用清晰的背景色
        self.main_frame = ttk.Frame(self.root, style="MainContent.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置UI结构，调整初始化顺序
        self.setup_menu()
        self.setup_nav_buttons()
        self.setup_status_bar()  # 先初始化状态栏，确保status_var可用
        self.setup_content_area()  # 再初始化内容区
        
        # 验证UI组件是否正确创建
        self.validate_ui_components()
        
        # 强制更新UI，确保变更生效
        self.root.update_idletasks()
        
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
            {"text": "批量创建文件", "command": lambda: self.switch_tab(0)},
            {"text": "批量创建文件夹", "command": lambda: self.switch_tab(1)},
            {"text": "批量创建工作表", "command": lambda: self.switch_tab(2)},
            {"text": "批量重命名", "command": lambda: self.switch_tab(3)},
            {"text": "批量移动/复制", "command": lambda: self.switch_tab(4)}
        ]
        
        # 创建按钮
        for i, opt in enumerate(nav_options):
            btn = ttk.Button(
                self.nav_frame,
                text=opt["text"],
                command=opt["command"],
                style="Tab.TButton",
                width=15
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
        # 创建主内容框架，使用带有明显背景色的样式
        self.content_frame = ttk.Frame(self.main_frame, style="MainContent.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))  # 顶部和侧面有内边距，底部无内边距
        
        # 创建一个框架来容纳所有标签页内容，使用明确的样式
        self.tab_contents = ttk.Frame(self.content_frame, style="TabContent.TFrame")
        self.tab_contents.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页，但初始不显示
        self.tabs = []
        try:
            self.tabs = [
                CreateFilesTab(self.tab_contents, dnd_available=self.dnd_available),
                CreateDirsTab(self.tab_contents),
                CreateSheetsTab(self.tab_contents),
                RenameTab(self.tab_contents),
                MoveCopyTab(self.tab_contents)
            ]
            
            # 初始设置所有标签页为隐藏
            for tab in self.tabs:
                tab.pack_forget()
                # 为每个标签页添加内边距和边框
                tab.configure(padding=10)
            
            self.logger.info(f"成功创建 {len(self.tabs)} 个标签页")
        except Exception as e:
            self.logger.error(f"创建标签页失败: {str(e)}")
            self.logger.error(f"异常详情: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        # 设置底部按钮区域，独立放在main_frame中，在状态栏之上
        self.setup_bottom_buttons()
        
        # 显示第一个标签页，确保它被正确加载
        if self.tabs and len(self.tabs) > 0:
            # 确保显示第一个标签页
            self.current_tab_index = 0
            self.tabs[0].pack(fill=tk.BOTH, expand=True)
            # 更新状态栏
            tab_names = ["批量创建文件", "批量创建文件夹", "批量创建工作表", "批量重命名", "批量移动/复制"]
            self.status_var.set(f"当前: {tab_names[0]}")
            # 标记选中的按钮
            self.mark_selected_button()
            
            self.logger.info("成功加载第一个标签页")
        else:
            self.logger.error("没有可用的标签页，界面可能显示为空白")
        
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
        
        # 添加一个边框来增强视觉区分
        self.tabs[index].configure(padding=10, borderwidth=1, relief=tk.GROOVE)
        
        # 更新当前标签页索引
        self.current_tab_index = index
        
        # 更新按钮样式
        self.mark_selected_button()
        
        # 更新状态栏
        tab_names = ["批量创建文件", "批量创建文件夹", "批量创建工作表", "批量重命名", "批量移动/复制"]
        self.status_var.set(f"当前: {tab_names[index]}")
        
        self.logger.info(f"切换到标签页: {tab_names[index]}")
    
    def mark_selected_button(self):
        """标记选中的按钮"""
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_tab_index:
                btn.configure(style="TabSelected.TButton")
                # 通过样式增加选中指示
                btn.state(["selected"])  # 添加selected状态
                
                # 可以考虑为按钮添加简单的边框效果
                try:
                    # 获取按钮在导航栏中的位置
                    btn_x = btn.winfo_x()
                    btn_y = btn.winfo_y()
                    btn_width = btn.winfo_width()
                    btn_height = btn.winfo_height()
                    
                    # 记录当前按钮位置，用于后续处理
                    btn.winfo_toplevel().update()  # 确保UI布局已更新
                    
                    # 记录选中按钮的日志信息
                    self.logger.debug(f"选中按钮 {i}: 位置({btn_x},{btn_y})，大小({btn_width}x{btn_height})")
                except Exception as e:
                    self.logger.error(f"获取按钮位置失败: {str(e)}")
            else:
                btn.configure(style="Tab.TButton")
                btn.state(["!selected"])  # 移除selected状态
        
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
        url = "https://batchfiletool.top"
        try:
            webbrowser.open(url)
        except Exception as e:
            self.logger.error(f"打开网站失败: {str(e)}")
            messagebox.showerror("错误", f"打开网站失败: {str(e)}")
    
    def center_dialog(self, dialog):
        """将对话框居中于主窗口"""
        self.root.update_idletasks()
        dialog.update_idletasks()
        
        # 获取主窗口和对话框的宽高
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        # 计算居中位置
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"+{x}+{y}")
    
    def show_donation(self):
        """显示赞助信息"""
        self.logger.info("显示赞助信息")
        
        # 创建自定义对话框
        donation_dialog = tk.Toplevel(self.root)
        donation_dialog.title("赞赏")
        donation_dialog.geometry("400x200")
        donation_dialog.resizable(False, False)
        donation_dialog.transient(self.root)  # 设置为主窗口的子窗口
        donation_dialog.grab_set()  # 模态对话框
        
        # 使用Frame容器
        frame = ttk.Frame(donation_dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加文本信息
        message = "感谢您使用批量文件处理工具!\n\n您的支持是我们持续改进的动力!\n\n如果有大的商机，可以通过点击关于、作者联系我。"
        message_label = ttk.Label(frame, text=message, wraplength=350, justify=tk.CENTER)
        message_label.pack(pady=(0, 20))
        
        # 添加捐赠链接
        def open_donation_link():
            webbrowser.open("https://ko-fi.com/etfminifatter")
            donation_dialog.destroy()
        
        donation_link = ttk.Label(frame, text="捐赠", foreground="blue", cursor="hand2")
        donation_link.pack()
        donation_link.bind("<Button-1>", lambda e: open_donation_link())
        
        # 添加样式，使文本显示为链接样式
        donation_link.configure(font=("Arial", 10, "underline"))
        
        # 居中显示对话框
        self.center_dialog(donation_dialog)
    
    def show_ads(self):
        """显示广告信息"""
        self.logger.info("显示广告信息")
        ads_info = """这是预留的一个广告位，准备后续可以靠软件上的广告位展示赚广告费，目前空缺，不知道怎么接入呢。"""
        messagebox.showinfo("广告", ads_info)
    
    def show_help(self):
        """显示帮助信息"""
        self.logger.info("显示帮助信息")
        help_info = """
        批量文件处理工具使用指南：
        
        1. 创建文件：批量创建空文件或带模板内容的文件
        2. 创建文件夹：批量创建目录结构，支持层级
        3. 创建工作表：批量创建Excel工作表
        4. 重命名：批量重命名文件，支持替换、添加前后缀等
        5. 移动/复制：批量移动或复制文件
        
        详细使用说明请访问官方网站。
        """
        messagebox.showinfo("帮助", help_info)
    
    def show_about(self):
        """显示关于信息"""
        self.logger.info("显示关于信息")
        
        # 创建自定义对话框
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("关于")
        about_dialog.geometry("450x280")
        about_dialog.resizable(False, False)
        about_dialog.transient(self.root)  # 设置为主窗口的子窗口
        about_dialog.grab_set()  # 模态对话框
        
        # 使用Frame容器
        frame = ttk.Frame(about_dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        title_label = ttk.Label(frame, text="批量文件处理工具 v1.0.0", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # 添加分隔线
        separator1 = ttk.Separator(frame, orient="horizontal")
        separator1.pack(fill="x", pady=5)
        
        # 添加描述
        desc_label = ttk.Label(frame, 
                              text="一个简单易用的批量文件处理工具，帮助您提高效率，节省你的时间", 
                              wraplength=400, 
                              justify=tk.CENTER)
        desc_label.pack(pady=15)
        
        # 添加分隔线
        separator2 = ttk.Separator(frame, orient="horizontal")
        separator2.pack(fill="x", pady=5)
        
        # 添加版权信息和作者信息
        info_frame = ttk.Frame(frame)
        info_frame.pack(pady=10)
        
        copyright_label = ttk.Label(info_frame, text="版权所有  作者: ")
        copyright_label.grid(row=0, column=0, sticky="e")
        
        # 添加作者链接
        def open_author_link():
            webbrowser.open("https://bento.me/etfminifatter")
            
        author_link = ttk.Label(info_frame, text="ETF迷你小富胖子", foreground="blue", cursor="hand2")
        author_link.grid(row=0, column=1, sticky="w")
        author_link.bind("<Button-1>", lambda e: open_author_link())
        author_link.configure(font=("Arial", 10, "underline"))
        
        # GitHub仓库链接
        github_label = ttk.Label(info_frame, text="GitHub仓库: ")
        github_label.grid(row=1, column=0, sticky="e", pady=(10, 0))
        
        def open_github_link():
            webbrowser.open("https://github.com/etfminifatter/batchprocessfiles")
            
        github_link = ttk.Label(info_frame, text="batchprocessfiles", foreground="blue", cursor="hand2")
        github_link.grid(row=1, column=1, sticky="w", pady=(10, 0))
        github_link.bind("<Button-1>", lambda e: open_github_link())
        github_link.configure(font=("Arial", 10, "underline"))
        
        # 居中显示对话框
        self.center_dialog(about_dialog)
    
    def update_tab_highlight(self):
        """更新标签页高亮线的位置"""
        if hasattr(self, 'nav_buttons') and self.nav_buttons and self.current_tab_index < len(self.nav_buttons):
            # 获取当前选中的按钮
            btn = self.nav_buttons[self.current_tab_index]
            
            # 更新高亮线位置
            if hasattr(self, 'tab_highlight') and self.tab_highlight and self.tab_highlight.winfo_exists():
                try:
                    # 计算按钮位置
                    btn_x = btn.winfo_x()
                    btn_y = btn.winfo_y()
                    btn_height = btn.winfo_height()
                    
                    # 更新左侧高亮线位置
                    self.tab_highlight.place(x=btn_x, y=btn_y+2, height=btn_height-4)
                    
                    # 强制更新UI
                    self.root.update_idletasks()
                except Exception as e:
                    self.logger.error(f"更新高亮线位置失败: {str(e)}")