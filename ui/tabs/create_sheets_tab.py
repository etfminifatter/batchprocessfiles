import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.excel_utils import create_sheets, read_sheet_names, read_column_headers, read_column_data
import os
import logging

class CreateSheetsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 初始化日志记录器
        self.logger = logging.getLogger("create_sheets_tab")
        self.logger.info("初始化创建工作表标签页")
        # 保存对root窗口的引用，用于访问剪贴板
        self.root = self.winfo_toplevel()
        self.setup_ui()
        self.logger.info("创建工作表标签页初始化完成")
        
    def setup_ui(self):
        # 输入区域
        input_frame = ttk.LabelFrame(self, text="输入区域")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输入方式选择
        input_method_frame = ttk.Frame(input_frame)
        input_method_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_method = tk.StringVar(value="direct")
        ttk.Radiobutton(input_method_frame, text="直接输入", variable=self.input_method, 
                       value="direct", command=self.toggle_input_method).pack(side=tk.LEFT)
        ttk.Radiobutton(input_method_frame, text="从Excel导入", variable=self.input_method, 
                       value="excel", command=self.toggle_input_method).pack(side=tk.LEFT)
        
        # 直接输入区域
        self.direct_input_frame = ttk.Frame(input_frame)
        self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.text_input = tk.Text(self.direct_input_frame, height=5)
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.direct_input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="从剪贴板粘贴", style="Auxiliary.TButton", command=self.paste_from_clipboard).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清空", style="Auxiliary.TButton", command=self.clear_input).pack(side=tk.LEFT)
        
        # Excel导入区域 - 修改布局
        self.excel_input_frame = ttk.Frame(input_frame)
        
        # 第一行：Excel文件选择
        file_select_frame = ttk.Frame(self.excel_input_frame)
        file_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_select_frame, text="导入Excel:").pack(side=tk.LEFT, padx=(0, 5))
        self.excel_path = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.excel_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_select_frame, text="浏览", style="Auxiliary.TButton", command=self.browse_excel).pack(side=tk.LEFT, padx=5)
        
        # 第二行：读取工作表按钮和工作表设置
        sheet_settings_frame = ttk.Frame(self.excel_input_frame)
        sheet_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.read_sheets_button = ttk.Button(sheet_settings_frame, text="读取工作表", style="Auxiliary.TButton", 
                                            command=self.read_excel_sheets)
        self.read_sheets_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 工作表名称列选择区域
        self.sheet_column_frame = ttk.Frame(sheet_settings_frame)
        self.sheet_column_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(self.sheet_column_frame, text="工作表名称列:").pack(side=tk.LEFT, padx=(0, 5))
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(self.sheet_column_frame, textvariable=self.column_var, width=20, state='readonly')
        self.column_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.column_combo.bind("<<ComboboxSelected>>", self.on_column_selected)
        
        # 包含表头勾选框
        self.has_header_var = tk.BooleanVar(value=True)
        header_checkbox_frame = ttk.Frame(sheet_settings_frame)
        header_checkbox_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        self.header_checkbox = ttk.Checkbutton(
            header_checkbox_frame, 
            text="跳过表头行", 
            variable=self.has_header_var, 
            command=self.header_checkbox_clicked
        )
        self.header_checkbox.pack(side=tk.LEFT)
        
        # 添加帮助提示按钮
        help_button = ttk.Button(
            header_checkbox_frame, 
            text="?", 
            width=2, 
            command=lambda: messagebox.showinfo(
                "跳过表头行说明", 
                "勾选此复选框时，将不显示Excel中的第一行（表头行）\n"
                "不勾选时，将显示包括表头在内的所有数据"
            )
        )
        help_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # 表格格式设置
        format_frame = ttk.LabelFrame(self, text="表格格式设置")
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 标题行设置区域
        title_section = ttk.Frame(format_frame)
        title_section.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)
        
        self.enable_title = tk.BooleanVar(value=False)
        ttk.Checkbutton(title_section, text="创建标题行", variable=self.enable_title, 
                       command=self.toggle_title).pack(anchor=tk.W)
        
        # 标题行输入框直接放在标题行设置区域下
        self.title_frame = ttk.Frame(title_section)
        ttk.Label(self.title_frame, text="标题文本:").pack(side=tk.LEFT, padx=5)
        self.title_text = ttk.Entry(self.title_frame, width=40)
        self.title_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 表头行设置区域
        header_section = ttk.Frame(format_frame)
        header_section.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)
        
        self.enable_header = tk.BooleanVar(value=False)
        ttk.Checkbutton(header_section, text="创建表头行", variable=self.enable_header, 
                       command=self.toggle_header).pack(anchor=tk.W)
        
        # 表头行输入框直接放在表头行设置区域下，改为多行文本框
        self.header_frame = ttk.Frame(header_section)
        ttk.Label(self.header_frame, text="表头名称:").pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)
        ttk.Label(self.header_frame, text="(每行一个表头，按回车分隔)", font=("", 8)).pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.header_text = tk.Text(self.header_frame, height=4, width=40)
        self.header_text.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=2)
        
        # 输出设置区域
        output_frame = ttk.LabelFrame(self, text="输出设置")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输出文件
        file_frame = ttk.Frame(output_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="输出文件:").pack(side=tk.LEFT, padx=5)
        self.output_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.output_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="浏览", style="Auxiliary.TButton", command=self.browse_output).pack(side=tk.LEFT, padx=5)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(self, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览表格
        columns = ("序号", "工作表名称", "包含内容")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings")
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100)
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化界面状态
        self.toggle_input_method()
        self.toggle_title()
        self.toggle_header()
    
    def toggle_input_method(self):
        """切换输入方式"""
        if self.input_method.get() == "direct":
            # 如果从Excel模式切换到直接输入模式，并且之前没有导入数据，则尝试预览当前选中的列
            if not hasattr(self, 'excel_imported_data') and hasattr(self, 'column_var') and self.column_var.get():
                self.preview_selected_column()  # 先尝试预览选中的列数据
            
            # 显示直接输入框架
            self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
            self.excel_input_frame.pack_forget()
            
            # 如果已经从Excel导入了数据，则显示导入的数据（不管文本框是否为空）
            if hasattr(self, 'excel_imported_data'):
                # 记录详细的数据状态
                count = len(self.excel_imported_data)
                if count > 0:
                    data_preview = ", ".join(self.excel_imported_data[:3])
                    if count > 3:
                        data_preview += "..."
                    self.logger.debug(f"将显示的数据({count}项): {data_preview}")
                
                # 始终更新文本框内容，确保显示最新数据
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
                
                skip_header = self.has_header_var.get()
                self.logger.info(f"已将导入的Excel数据（{count}项）显示在文本框中，跳过表头: {skip_header}")
        else:
            # 从直接输入模式切换到Excel导入模式
            self.direct_input_frame.pack_forget()
            self.excel_input_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_title(self):
        """切换标题行"""
        if self.enable_title.get():
            self.title_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.title_frame.pack_forget()
    
    def toggle_header(self):
        """切换表头行"""
        if self.enable_header.get():
            self.header_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.header_frame.pack_forget()
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        try:
            text = self.root.clipboard_get()
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(1.0, text)
        except tk.TclError:
            messagebox.showerror("错误", "剪贴板为空或内容不可用")
    
    def clear_input(self):
        """清空输入"""
        self.text_input.delete(1.0, tk.END)
        # 不清除Excel导入的数据，这样切换后可以恢复
    
    def browse_excel(self):
        """浏览Excel文件"""
        self.logger.info("浏览Excel文件")
        filetypes = [
            ("Excel文件", "*.xlsx *.xls"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.excel_path.set(filename)
            self.logger.info(f"已选择Excel文件: {filename}")
            # 清空列选择下拉框
            self.column_combo['values'] = []
            self.column_var.set("")
    
    def read_excel_sheets(self):
        """读取Excel文件的工作表信息"""
        self.logger.info("读取Excel文件的工作表信息")
        # 检查文件是否存在
        excel_path = self.excel_path.get()
        if not excel_path:
            messagebox.showerror("错误", "请先选择Excel文件")
            return
        
        # 调用excel_utils中的函数读取工作表
        success, result = read_sheet_names(excel_path)
        
        if success:
            # 将工作表名称显示在界面上，允许选择一个工作表
            sheet_list_window = tk.Toplevel(self)
            sheet_list_window.title("选择一个工作表")
            sheet_list_window.geometry("300x400")
            
            # 显示工作表列表
            sheet_list_frame = ttk.Frame(sheet_list_window, padding=10)
            sheet_list_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(sheet_list_frame, text=f"在 {os.path.basename(excel_path)} 中找到 {len(result)} 个工作表:").pack(anchor=tk.W, pady=(0, 10))
            ttk.Label(sheet_list_frame, text="请选择一个工作表:").pack(anchor=tk.W, pady=(0, 5))
            
            # 创建列表框和滚动条
            list_frame = ttk.Frame(sheet_list_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            sheet_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
            sheet_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=sheet_listbox.yview)
            
            # 添加工作表名称
            for sheet in result:
                sheet_listbox.insert(tk.END, sheet)
            
            # 添加操作按钮
            button_frame = ttk.Frame(sheet_list_window)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="选择", 
                     command=lambda: self.select_sheet_and_show_columns(excel_path, sheet_listbox.curselection(), result, sheet_list_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", 
                     command=sheet_list_window.destroy).pack(side=tk.RIGHT, padx=5)
        else:
            messagebox.showerror("错误", result)
    
    def select_sheet_and_show_columns(self, excel_path, selection, sheet_list, window):
        """选择工作表并显示列名"""
        if not selection:
            messagebox.showwarning("警告", "请选择一个工作表")
            return
        
        # 获取选中的工作表名称
        self.selected_sheet = sheet_list[selection[0]]
        self.logger.info(f"已选择工作表: {self.selected_sheet}")
        
        # 关闭工作表选择窗口
        window.destroy()
        
        # 读取选中工作表的列名
        success, headers = read_column_headers(excel_path, self.selected_sheet)
        
        if not success:
            messagebox.showerror("错误", f"读取列名失败: {headers}")
            return
        
        if not headers:
            messagebox.showinfo("提示", "选中的工作表没有列名或者是空表")
            return
        
        # 记录表头信息用于调试
        headers_preview = ", ".join(headers[:5])
        if len(headers) > 5:
            headers_preview += "..."
        self.logger.debug(f"读取到的列名({len(headers)}个): {headers_preview}")
        
        # 更新列选择下拉框
        column_values = [f"{i+1}: {header}" for i, header in enumerate(headers)]
        self.column_combo['values'] = column_values
        self.column_var.set(column_values[0] if column_values else "")
        
        # 存储headers信息以供后续使用
        self.headers = headers
        
        # 保存当前模式
        old_mode = self.input_method.get()
        
        # 切换到Excel导入模式（确保显示Excel导入区域）
        self.input_method.set("excel")
        self.toggle_input_method()
        
        # 自动预览第一列数据，无需等待用户选择
        self.preview_selected_column()
        self.logger.info("已自动预览第一列数据")
        
        # 始终更新直接输入文本框，即使当前不在直接输入模式
        if hasattr(self, 'excel_imported_data'):
            # 暂存文本框内容
            old_text = self.text_input.get(1.0, tk.END).strip()
            
            # 更新文本框内容
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
            
            # 记录变化
            skip_header = self.has_header_var.get()
            current_count = len(self.excel_imported_data)
            self.logger.info(f"已更新直接输入文本框内容: {current_count}项, 跳过表头: {skip_header}")
            
            # 如果文本内容发生变化，记录下来
            if old_text != "\n".join(self.excel_imported_data):
                self.logger.debug("文本框内容已更新")
    
    def on_column_selected(self, event):
        """当用户选择列时触发预览"""
        self.logger.info(f"用户选择了列: {self.column_var.get()}")
        
        # 保存当前模式，以便在预览后恢复
        current_mode = self.input_method.get()
        
        # 预览选中列数据
        self.preview_selected_column()
        
        # 确保文本框内容一定更新，无论当前模式
        if current_mode != "direct":
            # 暂时改变模式以便能显示数据
            self.input_method.set("direct")
            # 更新文本框数据
            if hasattr(self, 'excel_imported_data'):
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
                self.logger.info("已在列选择后更新文本框内容")
            # 恢复原模式
            self.input_method.set(current_mode)
        else:
            # 如果已经是直接输入模式，确保数据立即显示
            if hasattr(self, 'excel_imported_data'):
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
                self.logger.info("已将新选择的列数据更新到文本框")
    
    def preview_selected_column(self):
        """预览当前选中列的数据"""
        if not hasattr(self, 'selected_sheet'):
            self.logger.warning("尚未选择工作表，无法预览数据")
            return
            
        if not hasattr(self, 'headers'):
            self.logger.warning("未读取到列头信息，无法预览数据")
            return
        
        # 获取选中的列信息
        selected_column = self.column_var.get()
        if not selected_column:
            self.logger.warning("未选择列，无法预览数据")
            return
        
        # 提取列索引
        try:
            column_index = int(selected_column.split(":")[0])
        except (ValueError, IndexError):
            self.logger.error(f"无法从'{selected_column}'提取列索引")
            return
        
        excel_path = self.excel_path.get()
        if not excel_path:
            self.logger.warning("Excel文件路径为空")
            return
            
        # 获取"跳过表头行"复选框状态
        skip_header = self.has_header_var.get()
        self.logger.debug(f"预览列 {column_index}，跳过表头: {skip_header}")
        
        # 读取列数据
        success, data = read_column_data(excel_path, self.selected_sheet, column_index, skip_header)
        
        if not success:
            self.logger.error(f"读取列数据失败: {data}")
            messagebox.showerror("错误", f"读取列数据失败: {data}")
            return
        
        # 保存导入的数据，以便在切换输入方式时使用
        if data:
            # 记录变更前的数据量(如果有)
            if hasattr(self, 'excel_imported_data'):
                old_count = len(self.excel_imported_data)
                self.logger.debug(f"原有数据量: {old_count}，更新为新数据量: {len(data)}")
            
            self.excel_imported_data = data
            self.logger.info(f"已读取 {len(data)} 条数据记录，跳过表头: {skip_header}")
            
            # 输出数据预览便于调试
            data_preview = ", ".join(data[:4])  # 只显示前4条
            if len(data) > 4:
                data_preview += "..."
            self.logger.debug(f"数据预览: {data_preview}")
            
            # 如果当前是直接输入模式，则显示数据
            if self.input_method.get() == "direct":
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(data))
                self.logger.info(f"已将数据显示在文本框中")
                
            self.logger.info(f"已预览 {len(data)} 个工作表名称")
        else:
            # 即使没有数据也创建一个空列表
            self.excel_imported_data = []
            self.logger.warning("读取到的数据为空")
            
            # 清空直接输入框
            if self.input_method.get() == "direct":
                self.text_input.delete(1.0, tk.END)
                
            messagebox.showinfo("提示", "未读取到任何数据，可能是该列为空或跳过表头设置不正确")
            self.logger.info("没有可用数据")
    
    def browse_output(self):
        """浏览输出文件"""
        filetypes = [
            ("Excel文件", "*.xlsx"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".xlsx")
        if filename:
            self.output_path.set(filename)
    
    def preview(self):
        """预览生成结果"""
        self.logger.info("开始预览生成结果")
        try:
            # 清空预览表格
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # 获取输入内容
            if self.input_method.get() == "direct":
                content = self.text_input.get(1.0, tk.END).strip().split('\n')
                sheet_names = [name.strip() for name in content if name.strip()]
                self.logger.info(f"从直接输入获取了 {len(sheet_names)} 个工作表名称")
            else:
                # 从Excel文件读取内容
                if hasattr(self, 'excel_imported_data') and self.excel_imported_data:
                    # 使用已导入的数据
                    sheet_names = self.excel_imported_data
                    self.logger.info(f"使用已导入的Excel数据，包含 {len(sheet_names)} 个工作表名称")
                else:
                    # 未导入数据，检查Excel路径
                    if not self.excel_path.get():
                        self.logger.warning("未选择Excel文件")
                        messagebox.showerror("错误", "请选择Excel文件或导入数据")
                        return
                    
                    # 读取Excel文件中的工作表名称，这是兜底方案
                    from utils.excel_utils import read_sheet_names
                    success, result = read_sheet_names(self.excel_path.get())
                    
                    if not success:
                        self.logger.error(f"读取Excel文件失败: {result}")
                        messagebox.showerror("错误", f"读取Excel文件失败: {result}")
                        return
                    
                    sheet_names = result
                    self.logger.info(f"从Excel文件获取了 {len(sheet_names)} 个工作表名称")
            
            if not sheet_names:
                self.logger.warning("没有有效的工作表名称")
                messagebox.showerror("错误", "没有有效的工作表名称")
                return
            
            # 获取输出文件路径
            output_path = self.output_path.get()
            if not output_path:
                self.logger.warning("未选择输出文件")
                messagebox.showerror("错误", "请选择输出文件")
                return
            
            # 获取包含内容
            content_list = []
            if self.enable_title.get() and self.title_text.get().strip():
                content_list.append(f"标题: {self.title_text.get().strip()}")
                self.logger.info(f"预览标题行: {self.title_text.get().strip()}")
                
            if self.enable_header.get():
                # 从多行文本框中获取表头
                header_lines = self.header_text.get("1.0", tk.END).strip().split('\n')
                if header_lines and any(line.strip() for line in header_lines):
                    headers = [line.strip() for line in header_lines if line.strip()]
                    content_list.append(f"表头: {', '.join(headers)}")
                    self.logger.info(f"预览表头行: {', '.join(headers)}")
            
            content_str = ", ".join(content_list) if content_list else "无附加内容"
            
            # 添加预览项
            for i, name in enumerate(sheet_names):
                self.preview_tree.insert("", tk.END, values=(i+1, name, content_str))
            
            self.logger.info(f"预览完成，显示了 {len(sheet_names)} 个工作表")
            
            # 更新输出文件显示
            if os.path.exists(output_path):
                # 如果文件已存在，显示警告
                messagebox.showwarning("警告", f"文件 {output_path} 已存在，执行时将更新该文件")
        
        except Exception as e:
            self.logger.error(f"预览失败: {str(e)}")
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def execute(self):
        """执行创建操作"""
        try:
            self.logger.info("开始执行创建工作表")
            # 获取输入内容
            if self.input_method.get() == "direct":
                content = self.text_input.get(1.0, tk.END).strip().split('\n')
                sheet_names = [name.strip() for name in content if name.strip()]
                self.logger.info(f"从直接输入获取了 {len(sheet_names)} 个工作表名称")
            else:
                # 从Excel文件读取内容
                if hasattr(self, 'excel_imported_data') and self.excel_imported_data:
                    # 使用已导入的数据
                    sheet_names = self.excel_imported_data
                    self.logger.info(f"使用已导入的Excel数据，包含 {len(sheet_names)} 个工作表名称")
                else:
                    # 未导入数据，检查Excel路径
                    if not self.excel_path.get():
                        self.logger.warning("未选择Excel文件")
                        messagebox.showerror("错误", "请选择Excel文件或导入数据")
                        return
                    
                    # 读取Excel文件中的工作表名称，这是兜底方案
                    from utils.excel_utils import read_sheet_names
                    success, result = read_sheet_names(self.excel_path.get())
                    
                    if not success:
                        self.logger.error(f"读取Excel文件失败: {result}")
                        messagebox.showerror("错误", f"读取Excel文件失败: {result}")
                        return
                    
                    sheet_names = result
                    self.logger.info(f"从Excel文件获取了 {len(sheet_names)} 个工作表名称")
            
            if not sheet_names:
                self.logger.warning("没有有效的工作表名称")
                messagebox.showerror("错误", "没有有效的工作表名称")
                return
            
            # 获取输出文件路径
            output_path = self.output_path.get()
            if not output_path:
                self.logger.warning("未选择输出文件")
                messagebox.showerror("错误", "请选择输出文件")
                return
            
            # 准备标题和表头
            title_row = None
            if self.enable_title.get() and self.title_text.get().strip():
                title_row = self.title_text.get().strip()
                self.logger.info(f"设置标题行: {title_row}")
            
            header_row = None
            if self.enable_header.get():
                # 从多行文本框中获取表头
                header_lines = self.header_text.get("1.0", tk.END).strip().split('\n')
                if header_lines and any(line.strip() for line in header_lines):
                    header_row = [line.strip() for line in header_lines if line.strip()]
                    self.logger.info(f"设置表头行: {header_row}")
            
            # 调用create_sheets函数创建工作表
            from utils.excel_utils import create_sheets
            self.logger.info(f"调用create_sheets函数，输出文件: {output_path}")
            success, message = create_sheets(output_path, sheet_names, title_row, header_row)
            
            if success:
                self.logger.info(f"创建工作表成功: {message}")
                messagebox.showinfo("成功", message)
            else:
                self.logger.error(f"创建工作表失败: {message}")
                messagebox.showerror("错误", message)
            
        except Exception as e:
            self.logger.error(f"创建工作表时发生异常: {str(e)}")
            messagebox.showerror("错误", f"创建工作表时发生错误: {str(e)}")
            
    def header_checkbox_clicked(self):
        """处理跳过表头复选框点击事件"""
        skip_header = self.has_header_var.get()
        self.logger.info(f"用户{'' if skip_header else '取消'}勾选了跳过表头行")
        
        # 预览数据
        self.preview_selected_column()
        
        # 无论当前是什么输入模式，都确保更新显示
        # 先保存当前输入模式
        current_mode = self.input_method.get()
        
        # 如果当前不是直接输入模式，临时切换到直接输入模式确保文本框更新
        if current_mode != "direct":
            # 暂存当前模式以便恢复
            self.input_method.set("direct")
            # 只更新文本框，不改变UI显示
            if hasattr(self, 'excel_imported_data'):
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
                self.logger.info(f"已在切换模式前更新文本框内容")
            # 恢复原模式
            self.input_method.set(current_mode)
        else:
            # 如果已经是直接输入模式，直接更新文本框
            if hasattr(self, 'excel_imported_data'):
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, "\n".join(self.excel_imported_data))
                self.logger.info(f"已根据跳过表头设置({skip_header})更新文本框内容")
        
        # 记录详细的数据状态
        if hasattr(self, 'excel_imported_data'):
            data_preview = ", ".join(self.excel_imported_data[:3])
            if len(self.excel_imported_data) > 3:
                data_preview += "..."
            self.logger.debug(f"更新后的数据({len(self.excel_imported_data)}项): {data_preview}")

# 以下是废弃的函数，保留以备后用

def use_selected_sheets(self, selection, sheet_list, window):
    """使用选中的工作表名称（废弃，保留以备后用）"""
    self.logger.info("使用选中的工作表名称")
    selected_sheets = [sheet_list[i] for i in selection]
    if not selected_sheets:
        messagebox.showwarning("警告", "请至少选择一个工作表")
        return
    
    # 清空现有输入
    self.text_input.delete(1.0, tk.END)
    # 插入选中的工作表名称
    self.text_input.insert(1.0, "\n".join(selected_sheets))
    # 切换到直接输入模式
    self.input_method.set("direct")
    self.toggle_input_method()
    # 关闭窗口
    window.destroy()
    self.logger.info(f"已导入 {len(selected_sheets)} 个工作表名称")
    
def use_all_sheets(self, sheet_list, window):
    """使用所有工作表名称（废弃，保留以备后用）"""
    self.logger.info("使用所有工作表名称")
    # 清空现有输入
    self.text_input.delete(1.0, tk.END)
    # 插入所有工作表名称
    self.text_input.insert(1.0, "\n".join(sheet_list))
    # 切换到直接输入模式
    self.input_method.set("direct")
    self.toggle_input_method()
    # 关闭窗口
    window.destroy()
    self.logger.info(f"已导入 {len(sheet_list)} 个工作表名称") 