import tkinter as tk
from tkinter import ttk

def configure_styles():
    """
    配置应用的样式
    
    Returns:
        ttk.Style: 配置好的样式对象
    """
    style = ttk.Style()
    
    # 配置基本颜色方案
    style.configure('TFrame', background='#f5f5f5')
    style.configure('TLabel', background='#f5f5f5')
    style.configure('TLabelframe', background='#f5f5f5')
    style.configure('TLabelframe.Label', background='#f5f5f5')
    
    # 配置按钮样式
    style.configure('TButton', 
        background='#f5f5f5',
        borderwidth=1,
        relief='raised',
        padding=(5, 2)
    )
    
    # 主要按钮样式
    style.configure('Primary.TButton',
        background='#0078D7',
        foreground='white',
        font=('Arial', 10, 'bold'),
        padding=(10, 5),
        relief='raised'
    )
    style.map('Primary.TButton',
        background=[('active', '#005fa1'), ('pressed', '#004c81')],
        relief=[('pressed', 'sunken')]
    )
    
    # 次要按钮样式
    style.configure('Secondary.TButton',
        background='#2196F3',
        foreground='white',
        padding=(10, 5)
    )
    style.map('Secondary.TButton',
        background=[('active', '#1976D2'), ('pressed', '#0D47A1')],
        relief=[('pressed', 'sunken')]
    )
    
    # 输入框样式
    style.configure('TEntry',
        padding=2,
        fieldbackground='white'
    )
    
    # 组合框样式
    style.configure('TCombobox',
        padding=2,
        fieldbackground='white'
    )
    
    # 表格样式
    style.configure('Treeview',
        background='white',
        fieldbackground='white'
    )
    style.map('Treeview',
        background=[('selected', '#0078D7')],
        foreground=[('selected', 'white')]
    )
    
    # 标签页样式
    style.configure('TNotebook',
        background='#f5f5f5',
        tabposition='n'
    )
    style.configure('TNotebook.Tab',
        background='#f5f5f5',
        padding=(10, 4)
    )
    style.map('TNotebook.Tab',
        background=[('selected', '#ffffff')],
        expand=[('selected', [1, 1, 1, 0])]
    )
    
    # 复选框样式
    style.configure('TCheckbutton',
        background='#f5f5f5'
    )
    
    # 单选按钮样式
    style.configure('TRadiobutton',
        background='#f5f5f5'
    )
    
    # 分隔符样式
    style.configure('TSeparator',
        background='#d1d1d1'
    )
    
    # 进度条样式
    style.configure('TProgressbar',
        background='#0078D7',
        troughcolor='#f5f5f5',
        borderwidth=0,
        thickness=10
    )
    
    return style 