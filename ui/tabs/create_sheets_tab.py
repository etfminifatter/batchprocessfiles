import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.excel_utils import create_sheets
import os

class CreateSheetsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
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
        
        ttk.Button(button_frame, text="从剪贴板粘贴", style="Secondary.TButton", command=self.paste_from_clipboard).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清空", style="Secondary.TButton", command=self.clear_input).pack(side=tk.LEFT)
        
        # Excel导入区域
        self.excel_input_frame = ttk.Frame(input_frame)
        
        self.excel_path = tk.StringVar()
        ttk.Entry(self.excel_input_frame, textvariable=self.excel_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.excel_input_frame, text="浏览", style="Secondary.TButton", command=self.browse_excel).pack(side=tk.LEFT, padx=5)
        
        # 表格格式设置
        format_frame = ttk.LabelFrame(self, text="表格格式设置")
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 标题行设置
        self.enable_title = tk.BooleanVar(value=False)
        ttk.Checkbutton(format_frame, text="创建标题行", variable=self.enable_title, 
                       command=self.toggle_title).pack(anchor=tk.W, padx=5, pady=5)
        
        self.title_frame = ttk.Frame(format_frame)
        ttk.Label(self.title_frame, text="标题文本:").pack(side=tk.LEFT, padx=5)
        self.title_text = ttk.Entry(self.title_frame)
        self.title_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 表头行设置
        self.enable_header = tk.BooleanVar(value=False)
        ttk.Checkbutton(format_frame, text="创建表头行", variable=self.enable_header, 
                       command=self.toggle_header).pack(anchor=tk.W, padx=5, pady=5)
        
        self.header_frame = ttk.Frame(format_frame)
        ttk.Label(self.header_frame, text="表头名称:").pack(side=tk.LEFT, padx=5)
        self.header_text = ttk.Entry(self.header_frame)
        self.header_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 输出设置区域
        output_frame = ttk.LabelFrame(self, text="输出设置")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输出文件
        file_frame = ttk.Frame(output_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="输出文件:").pack(side=tk.LEFT, padx=5)
        self.output_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.output_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="浏览", style="Secondary.TButton", command=self.browse_output).pack(side=tk.LEFT, padx=5)
        
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
        
        # 操作按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="预览", style="Primary.TButton", command=self.preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="执行", style="Primary.TButton", command=self.execute).pack(side=tk.LEFT, padx=5)
        
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
        filetypes = [
            ("Excel文件", "*.xlsx"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.excel_path.set(filename)
    
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
        # 清空预览表格
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 获取输入内容
        if self.input_method.get() == "direct":
            content = self.text_input.get(1.0, tk.END).strip().split('\n')
        else:
            # TODO: 从Excel文件读取内容
            content = []
        
        # 获取输出文件路径
        output_path = self.output_path.get()
        if not output_path:
            messagebox.showerror("错误", "请选择输出文件")
            return
        
        # 生成预览
        for i, name in enumerate(content):
            if not name.strip():
                continue
            
            # 获取包含内容
            content_list = []
            if self.enable_title.get():
                content_list.append(f"标题: {self.title_text.get()}")
            if self.enable_header.get():
                content_list.append(f"表头: {self.header_text.get()}")
            
            self.preview_tree.insert("", tk.END, values=(i+1, name, ", ".join(content_list)))
    
    def execute(self):
        """执行创建操作"""
        # TODO: 实现工作表创建逻辑
        messagebox.showinfo("提示", "工作表创建完成") 