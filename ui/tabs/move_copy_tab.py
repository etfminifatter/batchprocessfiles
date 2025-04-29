import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.file_utils import move_copy_files
import os
import logging
from datetime import datetime

logger = logging.getLogger("move_copy_tab")

class MoveCopyTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.files_to_process = []  # 存储选中的文件路径列表
        
        self.logger = logging.getLogger("move_copy_tab")
        self.logger.debug("初始化移动/复制标签页")
        self.setup_logger()
        self.setup_ui()
        
    def setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('move_copy_tab')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建日志目录
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建文件处理器
        log_file = os.path.join(log_dir, 'batch_file_tool.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 创建格式化器
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("移动/复制选项卡初始化")
        
    def setup_ui(self):
        """设置UI布局"""
        # 主框架
        main_frame = ttk.Frame(self, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部：操作区域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置左右布局
        left_pane = ttk.Frame(top_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_pane = ttk.Frame(top_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 设置左侧文件选择部分
        self.setup_file_selection(left_pane)
        
        # 设置右侧目标和选项部分
        right_top_frame = ttk.Frame(right_pane)
        right_top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.setup_target_path(right_top_frame)
        self.setup_options(right_top_frame)
        
        # 设置预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
        
        self.setup_preview_area(preview_frame)
        
        # 设置底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="执行", command=self.execute, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="预览", command=self.preview, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
    
    def setup_file_selection(self, parent):
        """设置文件选择区域"""
        # 文件选择区域框架
        selection_frame = ttk.LabelFrame(parent, text="文件选择")
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加文件和文件夹按钮
        ttk.Button(button_frame, text="添加文件", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加文件夹", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_selection).pack(side=tk.LEFT, padx=5)
        
        # 文件列表区域
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 文件树状视图
        columns = ("文件名", "路径")
        self.files_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        # 设置列标题
        self.files_tree.heading("文件名", text="文件名")
        self.files_tree.heading("路径", text="路径")
        
        # 设置列宽
        self.files_tree.column("文件名", width=150)
        self.files_tree.column("路径", width=300)
        
        # 添加滚动条
        y_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.files_tree.xview)
        self.files_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.files_tree, tearoff=0)
        self.context_menu.add_command(label="删除选中项", command=self.remove_selected_files)
        
        # 绑定右键菜单
        self.files_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_target_path(self, parent):
        """设置目标路径区域"""
        # 目标路径区域框架
        target_frame = ttk.LabelFrame(parent, text="目标路径")
        target_frame.pack(fill=tk.X, padx=(0, 0), pady=(0, 5))
        
        # 路径输入区域
        path_frame = ttk.Frame(target_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 标签和输入框并排
        self.target_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.target_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 浏览按钮
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_target_path)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def setup_options(self, parent):
        """设置操作选项区域"""
        # 操作选项区域框架
        options_frame = ttk.LabelFrame(parent, text="操作选项")
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # 操作类型选择
        operation_frame = ttk.Frame(options_frame)
        operation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(operation_frame, text="操作类型:").pack(side=tk.LEFT)
        
        # 操作类型单选按钮
        self.operation_type = tk.StringVar(value="copy")
        ttk.Radiobutton(operation_frame, text="复制", variable=self.operation_type, value="copy").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(operation_frame, text="移动", variable=self.operation_type, value="move").pack(side=tk.LEFT, padx=5)
        
        # 冲突处理选项
        conflict_frame = ttk.Frame(options_frame)
        conflict_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conflict_frame, text="冲突处理:").pack(side=tk.LEFT)
        
        self.conflict_action = tk.StringVar(value="询问")
        conflict_combobox = ttk.Combobox(conflict_frame, textvariable=self.conflict_action, width=12)
        conflict_combobox["values"] = ("询问", "覆盖", "跳过", "自动重命名")
        conflict_combobox["state"] = "readonly"
        conflict_combobox.pack(side=tk.LEFT, padx=(10, 0))
        
        # 保留文件结构选项
        structure_frame = ttk.Frame(options_frame)
        structure_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.preserve_structure = tk.BooleanVar(value=False)
        ttk.Checkbutton(structure_frame, text="保留文件夹结构", variable=self.preserve_structure).pack(anchor=tk.W)
    
    def setup_preview_area(self, parent):
        """设置预览区域"""
        # 预览表格
        columns = ("序号", "文件名", "源路径", "目标路径")
        self.preview_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        
        # 设置列标题
        for col in columns:
            self.preview_tree.heading(col, text=col)
            # 设置列宽
            if col == "序号":
                self.preview_tree.column(col, width=40, stretch=False)
            elif col == "文件名":
                self.preview_tree.column(col, width=120)
            else:
                self.preview_tree.column(col, width=250)
        
        # 添加滚动条
        y_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
    
    def add_files(self):
        """添加文件按钮回调"""
        try:
            filepaths = filedialog.askopenfilenames(title="选择文件", filetypes=[("所有文件", "*.*")])
            if filepaths:
                for filepath in filepaths:
                    self._add_file_to_tree(filepath)
                self.logger.info(f"已添加 {len(filepaths)} 个文件")
        except Exception as e:
            self.logger.error(f"添加文件时出错: {str(e)}")
            messagebox.showerror("错误", f"添加文件时出错: {str(e)}")
    
    def add_folder(self):
        """添加文件夹按钮回调"""
        try:
            folder = filedialog.askdirectory(title="选择文件夹")
            if folder:
                count = 0
                # 遍历文件夹中的所有文件
                for root, _, files in os.walk(folder):
                    for file in files:
                        filepath = os.path.join(root, file)
                        self._add_file_to_tree(filepath)
                        count += 1
                
                if count > 0:
                    self.logger.info(f"已添加文件夹 {folder} 中的 {count} 个文件")
                else:
                    messagebox.showinfo("提示", f"文件夹 {folder} 中没有文件")
        except Exception as e:
            self.logger.error(f"添加文件夹时出错: {str(e)}")
            messagebox.showerror("错误", f"添加文件夹时出错: {str(e)}")
    
    def _add_file_to_tree(self, filepath):
        """将文件添加到树状视图中"""
        if filepath not in self.files_to_process:
            self.files_to_process.append(filepath)
            
            # 获取文件名和目录
            filename = os.path.basename(filepath)
            directory = os.path.dirname(filepath)
            
            # 添加到树状视图
            self.files_tree.insert("", tk.END, values=(filename, directory))
    
    def clear_selection(self):
        """清空选择的文件"""
        self.files_to_process = []
        self.files_tree.delete(*self.files_tree.get_children())
        self.logger.info("已清空文件选择")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 确保鼠标右键点击在项目上
        item = self.files_tree.identify_row(event.y)
        if item:
            # 选中被点击的项目
            self.files_tree.selection_set(item)
            # 显示右键菜单
            self.context_menu.post(event.x_root, event.y_root)
    
    def remove_selected_files(self):
        """从列表中移除选中的文件"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            return
        
        # 移除选中项
        for item in selected_items:
            values = self.files_tree.item(item, "values")
            file_path = os.path.join(values[1], values[0])
            # 从文件列表中移除
            if file_path in self.files_to_process:
                self.files_to_process.remove(file_path)
            # 从树状视图中移除
            self.files_tree.delete(item)
        
        self.logger.info(f"已移除 {len(selected_items)} 个文件")
    
    def browse_target_path(self):
        """浏览目标路径按钮回调"""
        try:
            target_dir = filedialog.askdirectory(title="选择目标文件夹")
            if target_dir:
                self.target_path.set(target_dir)
                self.logger.info(f"已选择目标路径: {target_dir}")
        except Exception as e:
            self.logger.error(f"选择目标路径时出错: {str(e)}")
            messagebox.showerror("错误", f"选择目标路径时出错: {str(e)}")
    
    def _find_common_base_path(self, file_paths):
        """查找文件路径列表的公共基础路径"""
        if not file_paths:
            return ""
        
        # 分离每个路径的各个部分
        split_paths = [os.path.dirname(p).split(os.sep) for p in file_paths]
        
        # 查找公共前缀
        common_parts = []
        for parts in zip(*split_paths):
            if len(set(parts)) == 1:  # 所有路径在这一层级都相同
                common_parts.append(parts[0])
            else:
                break
        
        if not common_parts:
            return ""
        
        # 拼接公共路径
        return os.sep.join(common_parts)
    
    def preview(self):
        """预览移动/复制操作"""
        if not self.files_to_process:
            messagebox.showinfo("提示", "请先选择要处理的文件")
            return
        
        target_dir = self.target_path.get()
        if not target_dir:
            messagebox.showinfo("提示", "请选择目标路径")
            return
        
        # 获取操作参数
        operation = self.operation_type.get()
        preserve_structure = self.preserve_structure.get()
        
        # 清空预览表格
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        try:
            for i, file_path in enumerate(self.files_to_process, 1):
                # 获取原始文件名和目录
                filename = os.path.basename(file_path)
                source_dir = os.path.dirname(file_path)
                
                # 确定目标路径
                if preserve_structure:
                    # 如果保留文件结构，需要计算相对路径
                    # 查找公共基础路径
                    common_base = self._find_common_base_path(self.files_to_process)
                    if common_base and file_path.startswith(common_base):
                        rel_path = os.path.relpath(source_dir, common_base)
                        target_full_path = os.path.join(target_dir, rel_path, filename)
                    else:
                        # 没有共同基础，直接使用完整路径
                        target_full_path = os.path.join(target_dir, filename)
                else:
                    target_full_path = os.path.join(target_dir, filename)
                
                # 添加到预览表格
                self.preview_tree.insert("", tk.END, values=(i, filename, source_dir, os.path.dirname(target_full_path)))
            
            # 操作类型文本
            op_text = "复制" if operation == "copy" else "移动"
            self.logger.info(f"已预览 {len(self.files_to_process)} 个文件的{op_text}操作")
        except Exception as e:
            self.logger.error(f"预览操作时出错: {str(e)}")
            messagebox.showerror("错误", f"预览操作时出错: {str(e)}")
    
    def execute(self):
        """执行移动/复制操作"""
        if not self.files_to_process:
            messagebox.showinfo("提示", "请先选择要处理的文件")
            return
        
        target_dir = self.target_path.get()
        if not target_dir:
            messagebox.showinfo("提示", "请选择目标路径")
            return
        
        # 先预览，确保预览表格有数据
        if not self.preview_tree.get_children():
            self.preview()
        
        # 获取操作参数
        operation = self.operation_type.get()
        conflict_action = self.conflict_action.get()
        preserve_structure = self.preserve_structure.get()
        
        # 冲突处理选项映射
        conflict_map = {
            "询问": "ask",
            "覆盖": "overwrite",
            "跳过": "skip",
            "自动重命名": "rename"
        }
        
        # 操作类型文本
        op_text = "复制" if operation == "copy" else "移动"
        
        # 确认操作
        if not messagebox.askyesno("确认", f"确定要{op_text} {len(self.files_to_process)} 个文件吗？"):
            return
        
        try:
            # 调用文件工具类执行移动/复制
            success_count, failed_count = move_copy_files(
                self.files_to_process,
                target_dir,
                operation=operation,
                conflict_action=conflict_map.get(conflict_action, "ask"),
                preserve_structure=preserve_structure
            )
            
            # 显示操作结果
            if failed_count == 0:
                messagebox.showinfo("完成", f"成功{op_text} {success_count} 个文件")
                # 如果是移动操作，清空文件列表和预览
                if operation == "move":
                    self.clear_selection()
                    self.preview_tree.delete(*self.preview_tree.get_children())
            else:
                messagebox.showwarning("部分完成", f"已{op_text} {success_count} 个文件，{failed_count} 个文件失败")
        
        except Exception as e:
            self.logger.error(f"执行{op_text}操作时出错: {str(e)}")
            messagebox.showerror("错误", f"执行{op_text}操作时出错: {str(e)}") 