import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.excel_utils import create_sheets, read_sheet_names
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
        
        # Excel导入区域
        self.excel_input_frame = ttk.Frame(input_frame)
        
        self.excel_path = tk.StringVar()
        ttk.Entry(self.excel_input_frame, textvariable=self.excel_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.excel_input_frame, text="浏览", style="Auxiliary.TButton", command=self.browse_excel).pack(side=tk.LEFT, padx=5)
        
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
            self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
            self.excel_input_frame.pack_forget()
        else:
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
            # 添加一个预览按钮，直接读取Excel文件的工作表信息
            ttk.Button(self.excel_input_frame, text="读取工作表", style="Auxiliary.TButton", 
                      command=self.read_excel_sheets).pack(side=tk.LEFT, padx=5)
    
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
            # 将工作表名称显示在界面上
            sheet_list_window = tk.Toplevel(self)
            sheet_list_window.title("工作表列表")
            sheet_list_window.geometry("300x400")
            
            # 显示工作表列表
            sheet_list_frame = ttk.Frame(sheet_list_window, padding=10)
            sheet_list_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(sheet_list_frame, text=f"在 {os.path.basename(excel_path)} 中找到 {len(result)} 个工作表:").pack(anchor=tk.W, pady=(0, 10))
            
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
            
            ttk.Button(button_frame, text="使用选中项", 
                     command=lambda: self.use_selected_sheets(sheet_listbox.curselection(), result, sheet_list_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="使用全部", 
                     command=lambda: self.use_all_sheets(result, sheet_list_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", 
                     command=sheet_list_window.destroy).pack(side=tk.RIGHT, padx=5)
        else:
            messagebox.showerror("错误", result)
    
    def use_selected_sheets(self, selection, sheet_list, window):
        """使用选中的工作表名称"""
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
        """使用所有工作表名称"""
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
                if not self.excel_path.get():
                    self.logger.warning("未选择Excel文件")
                    messagebox.showerror("错误", "请选择Excel文件")
                    return
                
                # 读取Excel文件中的工作表名称
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
                if not self.excel_path.get():
                    self.logger.warning("未选择Excel文件")
                    messagebox.showerror("错误", "请选择Excel文件")
                    return
                
                # 读取Excel文件中的工作表名称
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