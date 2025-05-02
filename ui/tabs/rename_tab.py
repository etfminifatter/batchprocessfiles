import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.file_utils import rename_files
import os
import logging

class RenameTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.files_to_rename = []  # 存储选中的文件路径列表
        
        self.logger = logging.getLogger("rename_tab")
        self.logger.debug("初始化重命名标签页")
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        # 主框架
        main_frame = ttk.Frame(self, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部：操作区域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 设置左右布局
        left_pane = ttk.Frame(top_frame, width=400)  # 设置固定宽度
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_pane.pack_propagate(False)  # 防止子组件改变frame大小
        
        right_pane = ttk.Frame(top_frame, width=400)  # 设置固定宽度
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_pane.pack_propagate(False)  # 防止子组件改变frame大小
        
        # 左侧：文件选择
        self.setup_file_selection(left_pane)
        
        # 右侧：重命名规则
        self.setup_rename_rules(right_pane)
        
        # 预览区域 - 限制高度
        preview_frame = ttk.LabelFrame(main_frame, text="预览", height=150)
        preview_frame.pack(fill=tk.X, expand=False)
        preview_frame.pack_propagate(False)  # 防止子组件改变frame高度
        
        self.setup_preview_area(preview_frame)
    
    def setup_file_selection(self, parent):
        """设置文件选择区域"""
        # 文件选择区域框架
        file_frame = ttk.LabelFrame(parent, text="文件和文件夹选择")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 顶部按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # 按钮组 - 统一按钮间距和大小
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side=tk.LEFT)
        
        # 添加文件按钮
        add_files_btn = ttk.Button(btn_container, text="添加文件", command=self.add_files, style="Auxiliary.TButton")
        add_files_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 添加文件夹按钮
        add_folder_btn = ttk.Button(btn_container, text="添加文件夹", command=self.add_folder, style="Auxiliary.TButton")
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清空选择按钮
        clear_btn = ttk.Button(btn_container, text="清空选择", command=self.clear_selection, style="Auxiliary.TButton")
        clear_btn.pack(side=tk.LEFT, padx=0)
        
        # 添加提示标签
        tip_label = ttk.Label(button_frame, text="提示: 可反复点击添加文件/文件夹按钮添加多个项目", foreground="gray", font=("", 8))
        tip_label.pack(side=tk.RIGHT, padx=5)
        
        # 文件列表显示区域，使用grid布局管理滚动条
        list_container = ttk.Frame(file_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # 列配置
        columns = ("文件名", "路径")
        self.files_tree = ttk.Treeview(list_container, columns=columns, show="headings", selectmode="extended", height=8)
        
        # 设置列标题
        for col in columns:
            self.files_tree.heading(col, text=col)
            # 设置列宽
            if col == "文件名":
                self.files_tree.column(col, width=150)
            else:
                self.files_tree.column(col, width=300)
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(list_container, orient="horizontal", command=self.files_tree.xview)
        self.files_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局，使用grid而不是pack
        self.files_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置list_container的行列权重
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.files_tree, tearoff=0)
        self.context_menu.add_command(label="删除选中项", command=self.remove_selected_files)
        self.context_menu.add_command(label="全选", command=self.select_all_files)
        
        # 绑定右键菜单
        self.files_tree.bind("<Button-3>", self.show_context_menu)
        
        # 添加全选快捷键
        self.files_tree.bind("<Control-a>", self.select_all_files)
    
    def setup_rename_rules(self, parent):
        """设置重命名规则区域"""
        # 重命名规则区域框架
        rules_frame = ttk.LabelFrame(parent, text="重命名规则")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 查找和替换文本区域
        find_replace_frame = ttk.Frame(rules_frame)
        find_replace_frame.pack(fill=tk.X, padx=10, pady=(8, 5))
        
        # 查找文本
        find_frame = ttk.Frame(find_replace_frame)
        find_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(find_frame, text="查找文本:").pack(side=tk.LEFT, padx=(0, 5))
        self.find_text = tk.StringVar()
        ttk.Entry(find_frame, textvariable=self.find_text).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 替换文本
        replace_frame = ttk.Frame(find_replace_frame)
        replace_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(replace_frame, text="替换为:  ").pack(side=tk.LEFT, padx=(0, 5))
        self.replace_text = tk.StringVar()
        ttk.Entry(replace_frame, textvariable=self.replace_text).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 选项区域 - 使用分隔线增强视觉层次
        separator = ttk.Separator(rules_frame, orient="horizontal")
        separator.pack(fill=tk.X, padx=5, pady=5)
        
        # 选项区域
        options_frame = ttk.Frame(rules_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 大小写敏感和全词匹配选项
        self.case_sensitive = tk.BooleanVar(value=False)
        self.whole_word = tk.BooleanVar(value=False)
        self.use_regex = tk.BooleanVar(value=False)
        
        # 使用网格布局排列复选框
        checkboxes_frame = ttk.Frame(options_frame)
        checkboxes_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(checkboxes_frame, text="大小写敏感", variable=self.case_sensitive).grid(row=0, column=0, sticky="w", padx=(0, 15))
        ttk.Checkbutton(checkboxes_frame, text="全词匹配", variable=self.whole_word).grid(row=0, column=1, sticky="w", padx=0)
        ttk.Checkbutton(checkboxes_frame, text="使用正则表达式", variable=self.use_regex).grid(row=1, column=0, sticky="w", padx=(0, 15), pady=(5, 0), columnspan=2)
        
        # 应用范围选项
        scope_frame = ttk.LabelFrame(rules_frame, text="应用范围")
        scope_frame.pack(fill=tk.X, padx=10, pady=(5, 8))
        
        self.rename_scope = tk.StringVar(value="name_only")
        ttk.Radiobutton(scope_frame, text="仅文件名", variable=self.rename_scope, value="name_only").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Radiobutton(scope_frame, text="仅扩展名", variable=self.rename_scope, value="ext_only").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Radiobutton(scope_frame, text="文件名和扩展名", variable=self.rename_scope, value="both").pack(anchor=tk.W, padx=8, pady=2)
    
    def setup_preview_area(self, parent):
        """设置预览区域"""
        # 创建一个容器框架，用于设置预览表格和滚动条
        preview_container = ttk.Frame(parent)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览表格
        columns = ("序号", "原文件名", "新文件名", "路径")
        self.preview_tree = ttk.Treeview(preview_container, columns=columns, show="headings", selectmode="browse", height=5)
        
        # 设置列标题
        for col in columns:
            self.preview_tree.heading(col, text=col)
            # 设置列宽
            if col == "序号":
                self.preview_tree.column(col, width=40, stretch=False)
            elif col in ("原文件名", "新文件名"):
                self.preview_tree.column(col, width=150)
            else:  # 路径列
                self.preview_tree.column(col, width=350, stretch=True)
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(preview_container, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局，使用grid而不是pack
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置容器的行列权重
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
    
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
            folder_path = filedialog.askdirectory(title="选择文件夹")
            if folder_path:
                self._add_folder_to_tree(folder_path)
                self.logger.info(f"已添加文件夹: {folder_path}")
        except Exception as e:
            self.logger.error(f"添加文件夹时出错: {str(e)}")
            messagebox.showerror("错误", f"添加文件夹时出错: {str(e)}")
    
    def _add_file_to_tree(self, filepath):
        """添加文件到文件列表"""
        # 检查是否已添加此文件
        for item in self.files_tree.get_children():
            if self.files_tree.item(item, "values")[1] == filepath:
                return  # 文件已存在，不重复添加
        
        # 解析文件名和路径
        filename = os.path.basename(filepath)
        directory = os.path.dirname(filepath)
        
        # 添加到树状视图
        self.files_tree.insert("", tk.END, values=(filename, directory))
        
        # 添加到文件列表
        self.files_to_rename.append(filepath)
    
    def _add_folder_to_tree(self, folder_path):
        """添加文件夹到文件列表"""
        # 检查是否已添加此文件夹
        for item in self.files_tree.get_children():
            values = self.files_tree.item(item, "values")
            full_path = os.path.join(values[1], values[0]) if values[1] else values[0]
            if full_path == folder_path:
                self.logger.debug(f"文件夹已存在，不重复添加：{folder_path}")
                return  # 文件夹已存在，不重复添加
        
        # 规范化路径
        folder_path = os.path.normpath(folder_path)
        
        # 解析文件夹名和路径
        folder_name = os.path.basename(folder_path)
        parent_dir = os.path.dirname(folder_path)
        
        self.logger.debug(f"添加文件夹：{folder_name}，父目录：{parent_dir}")
        
        # 添加到树状视图
        self.files_tree.insert("", tk.END, values=(folder_name, parent_dir))
        
        # 添加到文件列表
        self.files_to_rename.append(folder_path)
    
    def clear_selection(self):
        """清空选择按钮回调"""
        self.files_tree.delete(*self.files_tree.get_children())
        self.files_to_rename = []
        self.logger.info("已清空所有选择的文件")
    
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
        """从列表中移除选中的文件或文件夹"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            return
        
        # 移除选中项
        removed_count = 0
        for item in selected_items:
            values = self.files_tree.item(item, "values")
            name = values[0]
            directory = values[1]
            
            # 构建完整路径
            full_path = os.path.join(directory, name)
            
            self.logger.debug(f"尝试移除项目：{full_path}")
            
            # 从文件列表中移除
            if full_path in self.files_to_rename:
                self.files_to_rename.remove(full_path)
                removed_count += 1
                self.logger.debug(f"已从files_to_rename列表移除：{full_path}")
            else:
                # 可能是因为路径格式不同导致的不匹配，尝试查找规范化路径
                norm_path = os.path.normpath(full_path)
                for i, path in enumerate(self.files_to_rename):
                    if os.path.normpath(path) == norm_path:
                        self.logger.debug(f"找到匹配的规范化路径，从列表移除：{path}")
                        self.files_to_rename.pop(i)
                        removed_count += 1
                        break
            
            # 从树状视图中移除
            self.files_tree.delete(item)
        
        item_type = "项目" if removed_count > 0 else "文件或文件夹"
        self.logger.info(f"已移除 {removed_count} 个{item_type}")
    
    def preview(self):
        """预览重命名操作"""
        if not self.files_to_rename:
            messagebox.showinfo("提示", "请先选择要重命名的文件或文件夹")
            return
        
        find_text = self.find_text.get()
        if not find_text:
            messagebox.showinfo("提示", "请输入要查找的文本")
            return
        
        # 获取重命名参数
        replace_text = self.replace_text.get()
        case_sensitive = self.case_sensitive.get()
        whole_word = self.whole_word.get()
        use_regex = self.use_regex.get()
        rename_scope = self.rename_scope.get()
        
        self.logger.info(f"开始预览重命名，查找文本：'{find_text}'，替换为：'{replace_text}'，范围：{rename_scope}")
        self.logger.info(f"参数：区分大小写={case_sensitive}，全词匹配={whole_word}，使用正则={use_regex}")
        
        # 清空预览表格
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        try:
            # 获取所有重命名预览信息
            for i, file_path in enumerate(self.files_to_rename, 1):
                # 判断是文件还是文件夹
                is_dir = os.path.isdir(file_path)
                dirname = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                if is_dir:
                    # 如果是文件夹，且选择了只修改扩展名，则跳过
                    if rename_scope == "ext_only":
                        self.logger.debug(f"文件夹不支持仅修改扩展名，跳过：{file_path}")
                        continue
                        
                    # 处理文件夹名称
                    if not use_regex:
                        if case_sensitive:
                            if whole_word:
                                import re
                                folder_pattern = r'\b' + re.escape(find_text) + r'\b'
                                new_name = re.sub(folder_pattern, replace_text, filename)
                            else:
                                new_name = filename.replace(find_text, replace_text)
                        else:
                            if whole_word:
                                import re
                                folder_pattern = r'\b' + re.escape(find_text) + r'\b'
                                new_name = re.sub(folder_pattern, replace_text, filename, flags=re.IGNORECASE)
                            else:
                                new_name = self._replace_case_insensitive(filename, find_text, replace_text)
                    else:
                        # 使用正则表达式
                        import re
                        flags = 0 if case_sensitive else re.IGNORECASE
                        new_name = re.sub(find_text, replace_text, filename, flags=flags)
                    
                    # 如果文件夹名称没有变化，则跳过
                    if new_name == filename:
                        continue
                    
                    # 添加到预览表格
                    self.preview_tree.insert("", tk.END, values=(i, filename, new_name, dirname))
                    self.logger.debug(f"添加文件夹重命名预览：{filename} -> {new_name}")
                else:
                    # 处理文件
                    # 分离文件名和扩展名
                    name_part, ext_part = os.path.splitext(filename)
                    
                    # 根据应用范围确定要替换的部分
                    if rename_scope == "name_only":
                        # 只替换文件名部分
                        if not use_regex:
                            if case_sensitive:
                                if whole_word:
                                    # 全词匹配需要考虑边界
                                    import re
                                    name_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_name = re.sub(name_pattern, replace_text, name_part)
                                else:
                                    new_name = name_part.replace(find_text, replace_text)
                            else:
                                if whole_word:
                                    import re
                                    name_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_name = re.sub(name_pattern, replace_text, name_part, flags=re.IGNORECASE)
                                else:
                                    new_name = self._replace_case_insensitive(name_part, find_text, replace_text)
                        else:
                            # 使用正则表达式
                            import re
                            flags = 0 if case_sensitive else re.IGNORECASE
                            new_name = re.sub(find_text, replace_text, name_part, flags=flags)
                        
                        new_filename = new_name + ext_part
                    
                    elif rename_scope == "ext_only":
                        # 只替换扩展名部分（不包括点）
                        ext_to_replace = ext_part[1:] if ext_part else ""
                        
                        if not use_regex:
                            if case_sensitive:
                                if whole_word:
                                    import re
                                    ext_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_ext = re.sub(ext_pattern, replace_text, ext_to_replace)
                                else:
                                    new_ext = ext_to_replace.replace(find_text, replace_text)
                            else:
                                if whole_word:
                                    import re
                                    ext_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_ext = re.sub(ext_pattern, replace_text, ext_to_replace, flags=re.IGNORECASE)
                                else:
                                    new_ext = self._replace_case_insensitive(ext_to_replace, find_text, replace_text)
                        else:
                            # 使用正则表达式
                            import re
                            flags = 0 if case_sensitive else re.IGNORECASE
                            new_ext = re.sub(find_text, replace_text, ext_to_replace, flags=flags)
                        
                        new_filename = name_part + ("." + new_ext if new_ext else "")
                    
                    else:  # "both"
                        # 替换整个文件名
                        if not use_regex:
                            if case_sensitive:
                                if whole_word:
                                    import re
                                    filename_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_filename = re.sub(filename_pattern, replace_text, filename)
                                else:
                                    new_filename = filename.replace(find_text, replace_text)
                            else:
                                if whole_word:
                                    import re
                                    filename_pattern = r'\b' + re.escape(find_text) + r'\b'
                                    new_filename = re.sub(filename_pattern, replace_text, filename, flags=re.IGNORECASE)
                                else:
                                    new_filename = self._replace_case_insensitive(filename, find_text, replace_text)
                        else:
                            # 使用正则表达式
                            import re
                            flags = 0 if case_sensitive else re.IGNORECASE
                            new_filename = re.sub(find_text, replace_text, filename, flags=flags)
                    
                    if new_filename == filename:
                        continue
                    
                    # 添加到预览表格
                    self.preview_tree.insert("", tk.END, values=(i, filename, new_filename, dirname))
                
            if not self.preview_tree.get_children():
                messagebox.showinfo("提示", "没有文件或文件夹需要重命名，请检查您的查找条件")
            else:
                self.logger.info(f"已预览 {len(self.preview_tree.get_children())} 个项目的重命名操作")
        
        except Exception as e:
            self.logger.error(f"预览重命名操作时出错: {str(e)}")
            messagebox.showerror("错误", f"预览重命名操作时出错: {str(e)}")
    
    def _replace_case_insensitive(self, text, find, replace):
        """不区分大小写的文本替换"""
        index = 0
        result = ""
        find_lower = find.lower()
        text_lower = text.lower()
        
        while index < len(text):
            match_index = text_lower.find(find_lower, index)
            if match_index == -1:
                # 没有更多匹配
                result += text[index:]
                break
            
            # 添加匹配前的文本
            result += text[index:match_index]
            # 添加替换文本
            result += replace
            # 更新索引
            index = match_index + len(find)
        
        return result
    
    def execute(self):
        """执行重命名操作"""
        # 获取预览中的项目
        preview_items = self.preview_tree.get_children()
        if not preview_items:
            messagebox.showinfo("提示", "没有可重命名的项目，请先预览")
            return
        
        # 确认操作
        item_count = len(preview_items)
        if not messagebox.askyesno("确认", f"确定要重命名 {item_count} 个项目吗？"):
            return
        
        # 收集需要重命名的文件路径和新名称
        files_to_rename = []
        for item in preview_items:
            values = self.preview_tree.item(item, "values")
            # 值顺序：序号、原文件名、新文件名、路径
            orig_name = values[1]
            new_name = values[2]
            dirname = values[3]
            
            # 构建完整路径
            old_path = os.path.join(dirname, orig_name)
            files_to_rename.append(old_path)
        
        # 获取重命名参数
        find_text = self.find_text.get()
        replace_text = self.replace_text.get()
        case_sensitive = self.case_sensitive.get()
        whole_word = self.whole_word.get()
        use_regex = self.use_regex.get()
        rename_scope = self.rename_scope.get()
        
        try:
            # 执行重命名
            renamed_count = rename_files(
                files_to_rename, 
                find_text,
                replace_text,
                case_sensitive, 
                whole_word, 
                use_regex, 
                rename_scope
            )
            
            # 显示结果
            messagebox.showinfo("完成", f"重命名操作完成，成功重命名 {renamed_count} 个项目")
            self.logger.info(f"重命名操作完成，成功：{renamed_count}/{item_count}")
            
            # 刷新文件列表
            self.refresh_file_list()
        
            # 清空预览
            self.preview_tree.delete(*self.preview_tree.get_children())
            
        except Exception as e:
            self.logger.error(f"执行重命名操作时出错: {str(e)}")
            messagebox.showerror("错误", f"执行重命名操作时出错: {str(e)}")
    
    def refresh_file_list(self):
        """刷新文件列表，移除不存在的文件和文件夹"""
        # 清空现有列表
        self.files_tree.delete(*self.files_tree.get_children())
        
        # 过滤掉不存在的文件和文件夹
        original_count = len(self.files_to_rename)
        self.files_to_rename = [f for f in self.files_to_rename if os.path.exists(f)]
        filtered_count = original_count - len(self.files_to_rename)
        
        if filtered_count > 0:
            self.logger.info(f"移除了 {filtered_count} 个不存在的项目")
        
        # 重新添加存在的文件和文件夹
        for file_path in self.files_to_rename:
            is_dir = os.path.isdir(file_path)
            filename = os.path.basename(file_path)
            directory = os.path.dirname(file_path)
            
            self.logger.debug(f"刷新添加{'文件夹' if is_dir else '文件'}：{filename}, 路径：{directory}")
            self.files_tree.insert("", tk.END, values=(filename, directory)) 
    
    def select_all_files(self, event=None):
        """选择所有文件和文件夹"""
        for item in self.files_tree.get_children():
            self.files_tree.selection_add(item)
        return "break"  # 阻止默认行为 