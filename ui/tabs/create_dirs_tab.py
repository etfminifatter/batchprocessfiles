import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.file_utils import create_dirs
import os

class CreateDirsTab(ttk.Frame):
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
        ttk.Radiobutton(input_method_frame, text="从文件导入", variable=self.input_method, 
                       value="file", command=self.toggle_input_method).pack(side=tk.LEFT)
        
        # 直接输入区域
        self.direct_input_frame = ttk.Frame(input_frame)
        self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.text_input = tk.Text(self.direct_input_frame, height=5)
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.direct_input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="从剪贴板粘贴", style="Auxiliary.TButton", command=self.paste_from_clipboard).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清空", style="Auxiliary.TButton", command=self.clear_input).pack(side=tk.LEFT)
        
        # 文件导入区域
        self.file_input_frame = ttk.Frame(input_frame)
        
        self.file_path = tk.StringVar()
        ttk.Entry(self.file_input_frame, textvariable=self.file_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.file_input_frame, text="浏览", style="Auxiliary.TButton", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # 层级结构设置
        hierarchy_frame = ttk.LabelFrame(self, text="层级结构设置")
        hierarchy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.enable_hierarchy = tk.BooleanVar(value=False)
        ttk.Checkbutton(hierarchy_frame, text="启用层级结构", variable=self.enable_hierarchy, 
                       command=self.toggle_hierarchy).pack(anchor=tk.W, padx=5, pady=5)
        
        self.indent_frame = ttk.Frame(hierarchy_frame)
        ttk.Label(self.indent_frame, text="缩进空格数:").pack(side=tk.LEFT, padx=5)
        self.indent_spaces = ttk.Entry(self.indent_frame, width=5)
        self.indent_spaces.pack(side=tk.LEFT, padx=5)
        self.indent_spaces.insert(0, "4")
        
        # 命名规则区域
        rule_frame = ttk.LabelFrame(self, text="命名规则")
        rule_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.naming_rule = tk.StringVar(value="direct")
        ttk.Radiobutton(rule_frame, text="直接使用输入名称", variable=self.naming_rule, 
                       value="direct", command=self.toggle_naming_rule).pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(rule_frame, text="自定义命名规则", variable=self.naming_rule, 
                       value="custom", command=self.toggle_naming_rule).pack(anchor=tk.W, padx=5, pady=5)
        
        # 自定义命名规则区域
        self.custom_rule_frame = ttk.Frame(rule_frame)
        
        ttk.Label(self.custom_rule_frame, text="命名模式:").pack(anchor=tk.W, padx=5, pady=5)
        self.rule_pattern = ttk.Entry(self.custom_rule_frame)
        self.rule_pattern.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.custom_rule_frame, text="变量说明: $NAME=输入名称, $ISEQ=序号, $YYYY=年, $MM=月, $DD=日").pack(anchor=tk.W, padx=5, pady=5)
        
        # 序号设置
        seq_frame = ttk.Frame(self.custom_rule_frame)
        seq_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(seq_frame, text="起始值:").pack(side=tk.LEFT, padx=5)
        self.start_value = ttk.Entry(seq_frame, width=5)
        self.start_value.pack(side=tk.LEFT, padx=5)
        self.start_value.insert(0, "1")
        
        ttk.Label(seq_frame, text="步长:").pack(side=tk.LEFT, padx=5)
        self.step = ttk.Entry(seq_frame, width=5)
        self.step.pack(side=tk.LEFT, padx=5)
        self.step.insert(0, "1")
        
        ttk.Label(seq_frame, text="位数:").pack(side=tk.LEFT, padx=5)
        self.digits = ttk.Entry(seq_frame, width=5)
        self.digits.pack(side=tk.LEFT, padx=5)
        self.digits.insert(0, "3")
        
        # 输出设置区域
        output_frame = ttk.LabelFrame(self, text="输出设置")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 目标路径
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.target_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.target_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text="浏览", style="Auxiliary.TButton", command=self.browse_target_path).pack(side=tk.LEFT, padx=5)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(self, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览表格
        columns = ("序号", "原始输入", "生成目录名", "完整路径")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings")
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100)
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化界面状态
        self.toggle_input_method()
        self.toggle_naming_rule()
        self.toggle_hierarchy()
    
    def toggle_input_method(self):
        """切换输入方式"""
        if self.input_method.get() == "direct":
            self.direct_input_frame.pack(fill=tk.X, padx=5, pady=5)
            self.file_input_frame.pack_forget()
        else:
            self.direct_input_frame.pack_forget()
            self.file_input_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_naming_rule(self):
        """切换命名规则"""
        if self.naming_rule.get() == "direct":
            self.custom_rule_frame.pack_forget()
        else:
            self.custom_rule_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_hierarchy(self):
        """切换层级结构"""
        if self.enable_hierarchy.get():
            self.indent_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.indent_frame.pack_forget()
    
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
    
    def browse_file(self):
        """浏览文件"""
        filetypes = [
            ("文本文件", "*.txt"),
            ("CSV文件", "*.csv"),
            ("Excel文件", "*.xlsx"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
    
    def browse_target_path(self):
        """浏览目标路径"""
        path = filedialog.askdirectory()
        if path:
            self.target_path.set(path)
    
    def preview(self):
        """预览生成结果"""
        # 清空预览表格
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 获取输入内容
        if self.input_method.get() == "direct":
            content = self.text_input.get(1.0, tk.END).strip().split('\n')
        else:
            # TODO: 从文件读取内容
            content = []
        
        # 获取目标路径
        target_path = self.target_path.get()
        if not target_path:
            messagebox.showerror("错误", "请选择目标路径")
            return
        
        # 生成预览
        for i, name in enumerate(content):
            if not name.strip():
                continue
                
            if self.naming_rule.get() == "direct":
                new_name = name
            else:
                # TODO: 根据自定义规则生成新名称
                new_name = name
            
            full_path = os.path.join(target_path, new_name)
            self.preview_tree.insert("", tk.END, values=(i+1, name, new_name, full_path))
    
    def execute(self):
        """执行创建操作"""
        # TODO: 实现目录创建逻辑
        messagebox.showinfo("提示", "目录创建完成") 