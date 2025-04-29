import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from utils.file_utils import create_files
import os
import csv
import logging

class CreateFilesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger("create_files_tab")
        self.setup_ui()
        self.setup_drag_drop()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部分：文件输入和设置
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 设置左右布局
        left_pane = ttk.Frame(top_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_pane = ttk.Frame(top_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 设置各部分
        self.setup_input_area(left_pane)      # 左侧：输入区域
        self.setup_naming_rules(right_pane)   # 右上：命名规则
        self.setup_output_settings(right_pane) # 右下：输出设置
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_preview_area(preview_frame)
    
    def setup_input_area(self, parent):
        """设置输入区域"""
        input_frame = ttk.LabelFrame(parent, text="输入")
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入方式选择
        method_frame = ttk.Frame(input_frame)
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(method_frame, text="输入方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_method = tk.StringVar(value="direct")
        ttk.Radiobutton(method_frame, text="直接输入", variable=self.input_method, value="direct", 
                       command=self.toggle_input_method).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="从文件导入", variable=self.input_method, value="file", 
                       command=self.toggle_input_method).pack(side=tk.LEFT, padx=5)
        
        # 直接输入框架
        self.direct_input_frame = ttk.Frame(input_frame)
        self.direct_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加多行文本输入框，带滚动条
        self.text_input = scrolledtext.ScrolledText(self.direct_input_frame, height=10, width=40, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # 设置右键菜单
        self.setup_context_menu()
        
        # 从文件导入框架
        self.file_input_frame = ttk.Frame(input_frame)
        
        file_select_frame = ttk.Frame(self.file_input_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.file_path, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_select_frame, text="浏览", command=self.browse_file, style="Auxiliary.TButton").pack(side=tk.LEFT, padx=(5, 0))
        
        # 文件预览区域
        ttk.Label(self.file_input_frame, text="文件内容预览:").pack(anchor=tk.W, pady=(5, 0))
        
        self.file_preview = scrolledtext.ScrolledText(self.file_input_frame, height=8, width=40, wrap=tk.WORD, state="disabled")
        self.file_preview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 默认显示直接输入
        self.toggle_input_method()
        
        # 设置文件拖放支持
        self.setup_drag_drop()
    
    def setup_naming_rules(self, parent):
        """设置命名规则区域"""
        naming_frame = ttk.LabelFrame(parent, text="命名规则")
        naming_frame.pack(fill=tk.X, padx=0, pady=(0, 5))
        
        # 命名方式选择
        method_frame = ttk.Frame(naming_frame)
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(method_frame, text="命名方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.naming_rule = tk.StringVar(value="direct")
        ttk.Radiobutton(method_frame, text="直接命名", variable=self.naming_rule, value="direct", 
                       command=self.toggle_naming_rule).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="自定义规则", variable=self.naming_rule, value="custom", 
                       command=self.toggle_naming_rule).pack(side=tk.LEFT, padx=5)
        
        # 直接命名框架（无需额外设置，直接使用输入的名称）
        self.direct_naming_frame = ttk.Frame(naming_frame)
        ttk.Label(self.direct_naming_frame, text="将直接使用输入的文件名").pack(pady=10)
        
        # 自定义命名规则框架
        self.custom_naming_frame = ttk.Frame(naming_frame)
        
        rule_entry_frame = ttk.Frame(self.custom_naming_frame)
        rule_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rule_entry_frame, text="命名规则:").pack(side=tk.LEFT)
        self.rule_entry = ttk.Entry(rule_entry_frame)
        self.rule_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.rule_entry.insert(0, "prefix_$NAME_$ISEQ3")
        
        # 规则说明
        tip_frame = ttk.LabelFrame(self.custom_naming_frame, text="命名规则说明")
        tip_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tips = """
        $NAME - 替换为原始名称
        $ISEQ - 替换为序号，如 1, 2, 3...
        $ISEQ3 - 替换为固定位数序号，如 001, 002...
        $YYYY - 替换为年份
        $MM - 替换为月份
        $DD - 替换为日期
        """
        ttk.Label(tip_frame, text=tips, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # 序号设置
        seq_frame = ttk.Frame(self.custom_naming_frame)
        seq_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(seq_frame, text="起始序号:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.start_value = tk.StringVar(value="1")
        ttk.Entry(seq_frame, textvariable=self.start_value, width=5).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(seq_frame, text="序号步长:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.step_value = tk.StringVar(value="1")
        ttk.Entry(seq_frame, textvariable=self.step_value, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 默认显示直接命名
        self.toggle_naming_rule()
    
    def setup_output_settings(self, parent):
        """设置输出设置区域"""
        output_frame = ttk.LabelFrame(parent, text="输出设置")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # 目标路径
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(path_frame, text="目标路径:").pack(side=tk.LEFT)
        
        self.target_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.target_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_target_path, style="Auxiliary.TButton")
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 文件类型
        type_frame = ttk.Frame(output_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(type_frame, text="文件类型:").pack(side=tk.LEFT)
        
        self.file_type = tk.StringVar(value=".txt")
        file_type_combo = ttk.Combobox(type_frame, textvariable=self.file_type, width=15)
        file_type_combo['values'] = ('.txt', '.md', '.html', '.css', '.js', '.py', '.json', '.xlsx', '.csv')
        file_type_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 内容模板
        template_frame = ttk.LabelFrame(output_frame, text="内容模板 (可选)")
        template_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.content_template = scrolledtext.ScrolledText(template_frame, height=5, width=30, wrap=tk.WORD)
        self.content_template.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 模板说明
        ttk.Label(template_frame, text="使用 ${NAME} 替换为文件名, ${ISEQ} 替换为序号", 
                 foreground="gray").pack(anchor=tk.W)
    
    def setup_preview_area(self, parent):
        """设置预览区域"""
        # 预览表格
        columns = ("序号", "文件名", "路径")
        self.preview_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        
        # 设置列标题
        for col in columns:
            self.preview_tree.heading(col, text=col)
            if col == "序号":
                self.preview_tree.column(col, width=50, stretch=False)
            elif col == "文件名":
                self.preview_tree.column(col, width=200)
            else:
                self.preview_tree.column(col, width=350)
        
        # 添加滚动条
        y_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
    
    def setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="剪切", command=lambda: self.text_input.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="复制", command=lambda: self.text_input.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="粘贴", command=lambda: self.text_input.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.context_menu.add_command(label="清空", command=self.clear_input)
        
        self.text_input.bind("<Button-3>", self.show_context_menu)
    
    def setup_drag_drop(self):
        """设置拖放功能"""
        try:
            # 检查是否有TkinterDnD支持
            if hasattr(self.text_input, 'drop_target_register'):
                self.text_input.drop_target_register("DND_Files")
                self.text_input.dnd_bind("<<Drop>>", self.on_drop)
                self.logger.info("拖放功能设置成功")
                
                # 添加拖放提示
                hint_label = ttk.Label(
                    self.direct_input_frame, 
                    text="提示: 您可以直接拖放文件到此区域", 
                    foreground="gray",
                    background="#f5f5f5"
                )
                hint_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=(0, 5))
            else:
                self.logger.warning("没有找到拖放支持，请安装TkinterDnD2")
                
                # 添加安装建议
                hint_label = ttk.Label(
                    self.direct_input_frame, 
                    text="提示: 安装TkinterDnD2库以启用拖放功能", 
                    foreground="#FF6B6B",
                    background="#f5f5f5"
                )
                hint_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=(0, 5))
        except Exception as e:
            self.logger.warning(f"拖放功能设置失败: {str(e)}，可能需要安装TkinterDnD2")
    
    def on_drop(self, event):
        """处理拖放事件"""
        try:
            file_path = event.data
            # 移除引号和额外字符
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            
            self.logger.info(f"接收到拖放文件: {file_path}")
            
            # 根据当前选择的输入方式处理
            if self.input_method.get() == "direct":
                self.read_file_content(file_path)
            else:
                self.file_path.set(file_path)
        except Exception as e:
            self.logger.error(f"处理拖放失败: {str(e)}")
            messagebox.showerror("错误", f"处理拖放失败: {str(e)}")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def select_all(self):
        """全选文本"""
        self.text_input.tag_add(tk.SEL, "1.0", tk.END)
        self.text_input.mark_set(tk.INSERT, "1.0")
        self.text_input.see(tk.INSERT)
        return 'break'
    
    def toggle_input_method(self):
        """切换输入方式"""
        self.logger.debug(f"切换输入方式: {self.input_method.get()}")
        if self.input_method.get() == "direct":
            self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
            self.file_input_frame.pack_forget()
        else:
            self.direct_input_frame.pack_forget()
            self.file_input_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_naming_rule(self):
        """切换命名规则"""
        self.logger.debug(f"切换命名规则: {self.naming_rule.get()}")
        if self.naming_rule.get() == "direct":
            self.custom_naming_frame.pack_forget()
        else:
            self.custom_naming_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        try:
            self.logger.info("尝试从剪贴板粘贴")
            clipboard = self.clipboard_get()
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(1.0, clipboard)
            self.logger.info("粘贴成功，内容长度: {}".format(len(clipboard)))
        except Exception as e:
            self.logger.error(f"从剪贴板粘贴失败: {str(e)}")
            messagebox.showerror("错误", "剪贴板为空或内容不可用")
    
    def clear_input(self):
        """清空输入"""
        self.logger.debug("清空输入")
        self.text_input.delete(1.0, tk.END)
    
    def read_file_content(self, file_path):
        """读取文件内容"""
        self.logger.info(f"读取文件内容: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext in ['.txt', '.md', '.csv', '.py', '.html', '.css', '.js']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_input.delete(1.0, tk.END)
                    self.text_input.insert(1.0, content)
                    self.logger.info(f"成功读取文本文件，内容长度: {len(content)}")
                    
            elif ext in ['.xlsx', '.xls']:
                self.logger.info("检测到Excel文件，显示导入选项")
                self.input_method.set("file")
                self.toggle_input_method()
                self.file_path.set(file_path)
                
            else:
                self.logger.warning(f"不支持的文件类型: {ext}")
                messagebox.showwarning("警告", f"不支持的文件类型: {ext}")
                
        except Exception as e:
            self.logger.error(f"读取文件失败: {str(e)}")
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")
    
    def browse_file(self):
        """浏览文件"""
        self.logger.info("浏览文件")
        filetypes = [
            ("文本文件", "*.txt"),
            ("CSV文件", "*.csv"),
            ("Excel文件", "*.xlsx *.xls"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
            self.logger.info(f"已选择文件: {filename}")
    
    def browse_target_path(self):
        """浏览目标路径"""
        self.logger.info("浏览目标路径")
        path = filedialog.askdirectory()
        if path:
            self.target_path.set(path)
            self.logger.info(f"已选择目标路径: {path}")
    
    def get_input_names(self):
        """获取输入的名称列表"""
        self.logger.info("获取输入名称列表")
        if self.input_method.get() == "direct":
            # 从文本输入获取
            content = self.text_input.get(1.0, tk.END).strip()
            names = [line.strip() for line in content.split('\n') if line.strip()]
            self.logger.info(f"从直接输入获取了{len(names)}个名称")
            return names
        else:
            # 从文件获取
            file_path = self.file_path.get()
            if not file_path:
                self.logger.warning("未选择文件")
                messagebox.showerror("错误", "请选择一个文件")
                return []
            
            # 根据文件类型读取
            ext = os.path.splitext(file_path)[1].lower()
            names = []
            
            try:
                column_idx = int(self.column_index.get()) - 1
                has_header = self.file_has_header.get()
                
                if ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if has_header and lines:
                            lines = lines[1:]
                        names = [line.strip() for line in lines if line.strip()]
                
                elif ext == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        if has_header:
                            next(reader, None)  # 跳过表头
                        for row in reader:
                            if len(row) > column_idx:
                                name = row[column_idx].strip()
                                if name:
                                    names.append(name)
                
                elif ext in ['.xlsx', '.xls']:
                    import openpyxl
                    wb = openpyxl.load_workbook(file_path, read_only=True)
                    ws = wb.active
                    start_row = 2 if has_header else 1
                    for row in ws.iter_rows(min_row=start_row):
                        if len(row) > column_idx:
                            cell_value = row[column_idx].value
                            if cell_value:
                                names.append(str(cell_value).strip())
                    wb.close()
                
                self.logger.info(f"从文件{ext}中读取了{len(names)}个名称")
                return names
                
            except Exception as e:
                self.logger.error(f"从文件获取名称失败: {str(e)}")
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
                return []
    
    def preview(self):
        """预览生成结果"""
        self.logger.info("开始预览")
        try:
            # 清空预览表格
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # 获取输入名称
            names = self.get_input_names()
            if not names:
                self.logger.warning("没有输入名称")
                messagebox.showerror("错误", "请输入至少一个名称")
                return
            
            # 获取目标路径
            target_path = self.target_path.get()
            if not target_path:
                self.logger.warning("未选择目标路径")
                messagebox.showerror("错误", "请选择目标路径")
                return
            
            # 获取文件类型
            file_type = self.file_type.get()
            
            # 获取命名规则
            naming_rule = None
            if self.naming_rule.get() == "custom":
                naming_rule = self.rule_entry.get()
                self.logger.debug(f"使用自定义命名规则: {naming_rule}")
            
            # 获取序号设置
            try:
                start_value = int(self.start_value.get())
                step = int(self.step_value.get())
            except ValueError:
                self.logger.error("序号设置无效")
                messagebox.showerror("错误", "序号设置必须是整数")
                return
            
            # 生成预览
            from datetime import datetime
            import re
            
            for i, name in enumerate(names):
                seq = start_value + i * step
                seq_str = str(seq).zfill(3)
                
                if naming_rule:
                    new_name = naming_rule.replace('$NAME', name)
                    
                    # 处理序号，支持指定位数
                    seq_matches = re.findall(r'\$ISEQ(\d*)', new_name)
                    for seq_match in seq_matches:
                        if seq_match:
                            seq_digits = int(seq_match)
                            seq_formatted = str(seq).zfill(seq_digits)
                            new_name = new_name.replace(f'$ISEQ{seq_match}', seq_formatted)
                        else:
                            new_name = new_name.replace('$ISEQ', seq_str)
                    
                    # 处理日期变量
                    now = datetime.now()
                    new_name = new_name.replace('$YYYY', now.strftime('%Y'))
                    new_name = new_name.replace('$MM', now.strftime('%m'))
                    new_name = new_name.replace('$DD', now.strftime('%d'))
                else:
                    new_name = name
                
                # 添加文件类型扩展名
                filename = new_name + file_type
                full_path = os.path.join(target_path, filename)
                
                # 添加到预览表格，使用斑马条纹
                tags = ("oddrow",) if i % 2 == 1 else ()
                self.preview_tree.insert("", tk.END, values=(i+1, name, filename, full_path), tags=tags)
            
            self.logger.info(f"预览完成，显示了{len(names)}个文件")
        except Exception as e:
            self.logger.error(f"预览失败: {str(e)}")
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def execute(self):
        """执行创建文件"""
        self.logger.info("开始执行创建文件")
        try:
            # 获取输入名称
            names = self.get_input_names()
            if not names:
                self.logger.warning("没有输入名称")
                messagebox.showerror("错误", "请输入至少一个名称")
                return
            
            # 获取目标路径
            target_path = self.target_path.get()
            if not target_path:
                self.logger.warning("未选择目标路径")
                messagebox.showerror("错误", "请选择目标路径")
                return
            
            # 获取文件类型
            file_type = self.file_type.get()
            
            # 获取命名规则
            naming_rule = None
            if self.naming_rule.get() == "custom":
                naming_rule = self.rule_entry.get()
            
            # 获取序号设置
            try:
                start_value = int(self.start_value.get())
                step = int(self.step_value.get())
            except ValueError:
                self.logger.error("序号设置无效")
                messagebox.showerror("错误", "序号设置必须是整数")
                return
            
            # 获取内容模板
            content_template = self.content_template.get(1.0, tk.END).strip()
            if not content_template:
                content_template = None
            
            # 调用file_utils创建文件
            result, message = create_files(
                names=names,
                target_dir=target_path,
                file_type=file_type,
                content_template=content_template,
                naming_rule=naming_rule,
                start_value=start_value,
                step=step
            )
            
            if result:
                self.logger.info(f"创建文件成功: {message}")
                messagebox.showinfo("成功", message)
            else:
                self.logger.error(f"创建文件失败: {message}")
                messagebox.showerror("错误", message)
        except Exception as e:
            self.logger.error(f"执行创建文件失败: {str(e)}")
            messagebox.showerror("错误", f"执行失败: {str(e)}") 