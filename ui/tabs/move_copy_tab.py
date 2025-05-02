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
        self.files_to_process = []  # 存储选中的文件和文件夹路径列表
        
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
        left_pane = ttk.Frame(top_frame, width=400)  # 设置固定宽度
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_pane.pack_propagate(False)  # 防止子组件改变frame大小
        
        right_pane = ttk.Frame(top_frame, width=400)  # 设置固定宽度
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_pane.pack_propagate(False)  # 防止子组件改变frame大小
        
        # 设置左侧文件选择部分
        self.setup_file_selection(left_pane)
        
        # 设置右侧目标和选项部分
        right_top_frame = ttk.Frame(right_pane)
        right_top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.setup_target_path(right_top_frame)
        self.setup_options(right_top_frame)
        
        # 设置预览区域 - 限制高度
        preview_frame = ttk.LabelFrame(main_frame, text="预览", height=150)
        preview_frame.pack(fill=tk.X, expand=False, pady=(10, 5))
        preview_frame.pack_propagate(False)  # 防止子组件改变frame高度
        
        self.setup_preview_area(preview_frame)
    
    def setup_file_selection(self, parent):
        """设置文件选择区域"""
        # 文件选择区域框架
        selection_frame = ttk.LabelFrame(parent, text="文件选择")
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加文件和文件夹按钮
        ttk.Button(button_frame, text="添加文件", command=self.add_files, style="Auxiliary.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加文件夹", command=self.add_folder, style="Auxiliary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_selection, style="Auxiliary.TButton").pack(side=tk.LEFT, padx=5)
        
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
        
        # 添加目标路径输入和浏览按钮
        path_frame = ttk.Frame(target_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="目标路径:").pack(side=tk.LEFT, padx=5)
        self.target_path_var = tk.StringVar()
        self.target_path_entry = ttk.Entry(path_frame, textvariable=self.target_path_var)
        self.target_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_target_path, style="Auxiliary.TButton")
        browse_btn.pack(side=tk.LEFT, padx=5)
    
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
            elif col == "源路径":
                self.preview_tree.column(col, width=300)
            else:  # 目标路径
                self.preview_tree.column(col, width=300, stretch=True)
        
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
                added_count = 0
                for filepath in filepaths:
                    if self._add_file_to_tree(filepath):
                        added_count += 1
                self.logger.info(f"已添加 {added_count} 个文件")
        except Exception as e:
            self.logger.error(f"添加文件时出错: {str(e)}")
            messagebox.showerror("错误", f"添加文件时出错: {str(e)}")
    
    def add_folder(self):
        """添加文件夹按钮回调"""
        try:
            folder = filedialog.askdirectory(title="选择文件夹")
            if folder:
                # 直接添加文件夹而不是遍历其中的文件
                if self._add_folder_to_tree(folder):
                    self.logger.info(f"已添加文件夹: {folder}")
                else:
                    self.logger.info(f"文件夹已存在，未添加: {folder}")
        except Exception as e:
            self.logger.error(f"添加文件夹时出错: {str(e)}")
            messagebox.showerror("错误", f"添加文件夹时出错: {str(e)}")
    
    def _add_file_to_tree(self, filepath):
        """将文件添加到树状视图中"""
        # 规范化路径
        filepath = os.path.normpath(filepath)
        
        # 检查是否已存在
        exists = False
        for path in self.files_to_process:
            if os.path.normpath(path) == filepath:
                exists = True
                break
                
        if not exists:
            self.files_to_process.append(filepath)
            
            # 获取文件名和目录
            filename = os.path.basename(filepath)
            directory = os.path.dirname(filepath)
            
            # 添加到树状视图，标记为文件
            item_id = self.files_tree.insert("", tk.END, values=(filename, directory))
            # 标记为文件
            self.files_tree.item(item_id, tags=("file",))
            self.logger.debug(f"已添加文件到列表: {filepath}, 当前列表长度: {len(self.files_to_process)}")
            return True
        else:
            self.logger.debug(f"文件已存在，未添加: {filepath}")
            return False
    
    def _add_folder_to_tree(self, folderpath):
        """将文件夹添加到树状视图中"""
        # 规范化路径
        folderpath = os.path.normpath(folderpath)
        
        # 检查是否已存在
        exists = False
        for path in self.files_to_process:
            if os.path.normpath(path) == folderpath:
                exists = True
                break
                
        if not exists:
            self.files_to_process.append(folderpath)
            
            # 获取文件夹名和父目录
            foldername = os.path.basename(folderpath)
            parent_dir = os.path.dirname(folderpath)
            
            # 添加到树状视图，标记为文件夹
            item_id = self.files_tree.insert("", tk.END, values=(foldername, parent_dir))
            # 标记为文件夹
            self.files_tree.item(item_id, tags=("folder",))
            self.logger.debug(f"已添加文件夹到列表: {folderpath}, 当前列表长度: {len(self.files_to_process)}")
            return True
        else:
            self.logger.debug(f"文件夹已存在，未添加: {folderpath}")
            return False
    
    def clear_selection(self):
        """清空选择的文件和文件夹"""
        old_count = len(self.files_to_process)
        self.files_to_process = []
        self.files_tree.delete(*self.files_tree.get_children())
        self.logger.info(f"已清空文件和文件夹选择，移除了 {old_count} 个项目")
    
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
        """从列表中移除选中的文件和文件夹"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            return
        
        # 移除选中项
        removed_count = 0
        for item in selected_items:
            values = self.files_tree.item(item, "values")
            filename = values[0]
            directory = values[1]
            
            # 构建完整路径，避免直接拼接可能导致的问题
            if directory:
                path = os.path.normpath(os.path.join(directory, filename))
            else:
                path = os.path.normpath(filename)
            
            # 从文件列表中移除，使用规范化路径比较
            found = False
            for i, existing_path in enumerate(self.files_to_process):
                if os.path.normpath(existing_path) == path:
                    self.files_to_process.pop(i)
                    found = True
                    removed_count += 1
                    self.logger.debug(f"已从列表移除项目: {path}")
                    break
            
            # 记录未找到的情况
            if not found:
                self.logger.warning(f"无法在列表中找到路径: {path}")
                # 尝试直接使用filename作为备选查找方式
                for i, existing_path in enumerate(self.files_to_process):
                    if os.path.basename(existing_path) == filename:
                        self.files_to_process.pop(i)
                        self.logger.debug(f"通过文件名找到并移除项目: {existing_path}")
                        removed_count += 1
                        found = True
                        break
                
                if not found:
                    self.logger.warning(f"尝试所有方法后仍无法找到要移除的项目: {filename} in {directory}")
            
            # 从树状视图中移除
            self.files_tree.delete(item)
        
        # 打印当前列表的状态
        self.logger.info(f"已移除 {removed_count} 个项目，当前列表包含 {len(self.files_to_process)} 个项目")
        
        # 验证文件列表
        if len(self.files_to_process) != len(self.files_tree.get_children()):
            self.logger.warning(f"文件列表与树视图不一致！列表长度: {len(self.files_to_process)}，树项目数: {len(self.files_tree.get_children())}")
            self._synchronize_list_and_tree()
    
    def _synchronize_list_and_tree(self):
        """同步内部列表和树视图，确保它们一致"""
        self.logger.debug("开始同步列表和树视图")
        
        # 获取树视图中的所有项目
        tree_items = {}
        for item_id in self.files_tree.get_children():
            values = self.files_tree.item(item_id, "values")
            filename = values[0]
            directory = values[1]
            if directory:
                full_path = os.path.normpath(os.path.join(directory, filename))
            else:
                full_path = os.path.normpath(filename)
            tree_items[full_path] = item_id
        
        # 获取列表中的所有规范化路径
        list_paths = [os.path.normpath(p) for p in self.files_to_process]
        
        # 找出差异
        tree_only = set(tree_items.keys()) - set(list_paths)
        list_only = set(list_paths) - set(tree_items.keys())
        
        # 处理差异
        if tree_only:
            self.logger.warning(f"发现 {len(tree_only)} 个仅在树视图中存在的项目")
            for path in tree_only:
                # 从树视图中移除
                self.files_tree.delete(tree_items[path])
                self.logger.debug(f"从树视图中移除多余项目: {path}")
        
        if list_only:
            self.logger.warning(f"发现 {len(list_only)} 个仅在列表中存在的项目")
            # 过滤掉不存在的路径
            valid_list_only = [p for p in list_only if os.path.exists(p)]
            invalid_list_only = list_only - set(valid_list_only)
            
            # 移除不存在的路径
            new_list = [p for p in self.files_to_process if os.path.normpath(p) not in invalid_list_only]
            self.files_to_process = new_list
            
            # 添加有效的路径到树视图
            for path in valid_list_only:
                if os.path.isdir(path):
                    self._add_folder_to_tree(path)
                    self.logger.debug(f"添加目录到树视图: {path}")
                else:
                    self._add_file_to_tree(path)
                    self.logger.debug(f"添加文件到树视图: {path}")
        
        # 完成后再次验证
        if len(self.files_to_process) != len(self.files_tree.get_children()):
            self.logger.error(f"同步后仍不一致! 列表长度: {len(self.files_to_process)}，树项目数: {len(self.files_tree.get_children())}")
        else:
            self.logger.info("列表与树视图已成功同步")
    
    def browse_target_path(self):
        """浏览目标路径按钮回调"""
        try:
            target_dir = filedialog.askdirectory(title="选择目标文件夹")
            if target_dir:
                self.target_path_var.set(target_dir)
                self.logger.info(f"已选择目标路径: {target_dir}")
        except Exception as e:
            self.logger.error(f"选择目标路径时出错: {str(e)}")
            messagebox.showerror("错误", f"选择目标路径时出错: {str(e)}")
    
    def _find_common_base_path(self, file_paths):
        """查找文件路径列表的公共基础路径"""
        if not file_paths:
            return ""
        
        # 规范化路径
        normalized_paths = [os.path.normpath(p) for p in file_paths]
        
        # 分离每个路径的各个部分
        split_paths = [os.path.dirname(p).split(os.sep) for p in normalized_paths]
        
        # 查找公共前缀
        common_parts = []
        try:
            for parts in zip(*split_paths):
                if len(set(parts)) == 1:  # 所有路径在这一层级都相同
                    common_parts.append(parts[0])
                else:
                    break
        except Exception as e:
            self.logger.warning(f"查找公共路径时出错: {str(e)}")
            return ""
        
        if not common_parts:
            return ""
        
        # 拼接公共路径
        return os.sep.join(common_parts)
    
    def preview(self):
        """预览移动/复制操作"""
        # 首先确保列表和树视图一致
        if len(self.files_to_process) != len(self.files_tree.get_children()):
            self.logger.warning("预览前检测到列表与树视图不一致，执行同步")
            self._synchronize_list_and_tree()
        
        if not self.files_to_process:
            messagebox.showinfo("提示", "请先选择要处理的文件或文件夹")
            return
        
        target_dir = self.target_path_var.get()
        if not target_dir:
            messagebox.showinfo("提示", "请选择目标路径")
            return
        
        # 确保目标路径规范化
        target_dir = os.path.normpath(target_dir)
        
        # 获取操作参数
        operation = self.operation_type.get()
        preserve_structure = self.preserve_structure.get()
        
        # 清空预览表格
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        try:
            # 调试：打印当前列表内容
            self.logger.debug(f"预览开始，当前处理列表包含 {len(self.files_to_process)} 个项目")
            for i, path in enumerate(self.files_to_process):
                self.logger.debug(f"列表项 {i+1}: {path}")
            
            # 检查无效路径
            invalid_paths = [p for p in self.files_to_process if not os.path.exists(p)]
            if invalid_paths:
                self.logger.warning(f"预览时发现 {len(invalid_paths)} 个无效路径，将被排除")
                valid_paths = [p for p in self.files_to_process if os.path.exists(p)]
            else:
                valid_paths = self.files_to_process
            
            # 计算公共基础路径（用于保留结构）
            common_base = self._find_common_base_path(valid_paths) if preserve_structure else ""
            if preserve_structure and common_base:
                self.logger.debug(f"找到公共基础路径: {common_base}")
            
            # 添加到预览表格
            for i, path in enumerate(valid_paths, 1):
                # 规范化路径
                path = os.path.normpath(path)
                
                # 验证路径是否存在
                if not os.path.exists(path):
                    self.logger.warning(f"路径不存在，跳过预览: {path}")
                    continue
                
                # 获取原始名称和目录
                name = os.path.basename(path)
                source_dir = os.path.dirname(path)
                
                # 确定目标路径
                if preserve_structure and common_base:
                    # 如果保留文件结构，需要计算相对路径
                    if path.startswith(common_base):
                        rel_path = os.path.relpath(source_dir, common_base)
                        # 确保相对路径不以点开头
                        if rel_path == '.':
                            target_full_path = os.path.join(target_dir, name)
                        else:
                            target_full_path = os.path.join(target_dir, rel_path, name)
                    else:
                        # 没有共同基础，直接使用完整路径
                        target_full_path = os.path.join(target_dir, name)
                else:
                    target_full_path = os.path.join(target_dir, name)
                
                # 规范化目标路径
                target_full_path = os.path.normpath(target_full_path)
                
                # 判断是文件还是文件夹
                item_type = "文件夹" if os.path.isdir(path) else "文件"
                
                # 添加到预览表格
                item_id = self.preview_tree.insert("", tk.END, values=(i, name, source_dir, os.path.dirname(target_full_path)))
                
                # 根据类型设置标签
                if os.path.isdir(path):
                    self.preview_tree.item(item_id, tags=("folder",))
                else:
                    self.preview_tree.item(item_id, tags=("file",))
            
            # 操作类型文本
            op_text = "复制" if operation == "copy" else "移动"
            total_files = sum(1 for p in valid_paths if os.path.isfile(p))
            total_folders = sum(1 for p in valid_paths if os.path.isdir(p))
            
            self.logger.info(f"已预览 {op_text}操作: {total_files}个文件, {total_folders}个文件夹")
            
            # 检查列表和预览是否一致
            if len(self.preview_tree.get_children()) != len(valid_paths):
                self.logger.warning(f"预览不一致! 预览项目数: {len(self.preview_tree.get_children())}, 有效路径数: {len(valid_paths)}")
                
                # 如果有无效路径，现在是清理它们的好时机
                if invalid_paths:
                    self._cleanup_invalid_paths()
                
        except Exception as e:
            self.logger.error(f"预览操作时出错: {str(e)}")
            messagebox.showerror("错误", f"预览操作时出错: {str(e)}")
    
    def _cleanup_invalid_paths(self):
        """清理不存在的路径"""
        initial_count = len(self.files_to_process)
        
        # 清理不存在的路径
        valid_paths = []
        for path in self.files_to_process:
            norm_path = os.path.normpath(path)
            if os.path.exists(norm_path):
                valid_paths.append(norm_path)
            else:
                self.logger.warning(f"清理不存在的路径: {path}")
        
        # 更新列表
        if len(valid_paths) != initial_count:
            self.files_to_process = valid_paths
            self.logger.info(f"已清理 {initial_count - len(valid_paths)} 个无效路径，当前列表长度: {len(valid_paths)}")
            
            # 重建树视图
            self.files_tree.delete(*self.files_tree.get_children())
            for path in valid_paths:
                if os.path.isdir(path):
                    self._add_folder_to_tree(path)
                else:
                    self._add_file_to_tree(path)
    
    def execute(self):
        """执行移动/复制操作"""
        # 首先确保列表和树视图一致
        if len(self.files_to_process) != len(self.files_tree.get_children()):
            self.logger.warning("执行前检测到列表与树视图不一致，执行同步")
            self._synchronize_list_and_tree()
        
        if not self.files_to_process:
            messagebox.showinfo("提示", "请先选择要处理的文件或文件夹")
            return
        
        target_dir = self.target_path_var.get()
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
        
        # 统计文件和文件夹数量
        total_files = sum(1 for p in self.files_to_process if os.path.isfile(p))
        total_folders = sum(1 for p in self.files_to_process if os.path.isdir(p))
        
        # 检查路径是否有效
        invalid_paths = [p for p in self.files_to_process if not os.path.exists(p)]
        if invalid_paths:
            self.logger.warning(f"发现 {len(invalid_paths)} 个无效路径，将被自动移除")
            # 从列表中移除无效路径
            self.files_to_process = [p for p in self.files_to_process if os.path.exists(p)]
            # 重新同步UI
            self._synchronize_list_and_tree()
            # 更新统计数据
            total_files = sum(1 for p in self.files_to_process if os.path.isfile(p))
            total_folders = sum(1 for p in self.files_to_process if os.path.isdir(p))
        
        # 如果没有有效路径，则停止
        if not self.files_to_process:
            messagebox.showinfo("提示", "没有有效的文件或文件夹可处理")
            return
        
        # 确认操作
        confirm_msg = f"确定要{op_text}"
        if total_files > 0 and total_folders > 0:
            confirm_msg += f" {total_files}个文件和{total_folders}个文件夹吗？"
        elif total_folders > 0:
            confirm_msg += f" {total_folders}个文件夹吗？"
        else:
            confirm_msg += f" {total_files}个文件吗？"
            
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        try:
            # 记录将要处理的路径
            self.logger.debug(f"准备{op_text} {len(self.files_to_process)}个项目:")
            for i, path in enumerate(self.files_to_process):
                self.logger.debug(f"项目 {i+1}: {path} ({os.path.isdir(path) and '文件夹' or '文件'})")
            
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
                result_msg = f"成功{op_text} {success_count}个项目"
                messagebox.showinfo("完成", result_msg)
                # 如果是移动操作，清空文件列表和预览
                if operation == "move":
                    self.clear_selection()
                    self.preview_tree.delete(*self.preview_tree.get_children())
            else:
                messagebox.showwarning("部分完成", f"已{op_text} {success_count}个项目，{failed_count}个项目失败")
        
        except Exception as e:
            self.logger.error(f"执行{op_text}操作时出错: {str(e)}")
            messagebox.showerror("错误", f"执行{op_text}操作时出错: {str(e)}") 