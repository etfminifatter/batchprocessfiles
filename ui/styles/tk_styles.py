import tkinter as tk
from tkinter import ttk

def configure_styles():
    """
    配置应用的样式
    
    Returns:
        ttk.Style: 配置好的样式对象
    """
    style = ttk.Style()
    
    # 为tab添加左对齐
    def fixed_map(option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.

        # Style map overrides with other states, like focus, active, etc.
        # So we need to filter them out.
        return [elm for elm in style.map('TNotebook.Tab', query_opt=option)
                if elm[:2] != ('!disabled', '!selected')]
                
    try:
        # 这种修复可能对一些版本的Tkinter有效
        style.map('TNotebook.Tab', foreground=fixed_map('foreground'),
                 background=fixed_map('background'))
    except Exception:
        pass
    
    # 配置基本颜色方案 - 内容区域使用白色，边框区域使用灰色
    style.configure('TFrame', background='#FFFFFF')  # 改为白色背景
    style.configure('TLabel', background='#FFFFFF')  # 标签背景与内容区域一致
    
    # 更新LabelFrame样式 - 创建卡片式效果
    style.configure('TLabelframe', 
        background='#FFFFFF',  # 内容区域为白色
        borderwidth=1,
        relief='solid'  # 更明显的边框
    )
    style.configure('TLabelframe.Label', 
        background='#FFFFFF',
        font=('Arial', 10, 'bold')  # 加粗标题
    )
    
    # 普通按钮样式 - 灰色背景，黑色字体（直接输入、从文件导入、清空等按钮）
    style.configure('TButton', 
        background='#E6E6E6',  # 浅灰色背景
        foreground='#000000',  # 黑色文字
        borderwidth=1,
        relief='solid',  # 实线边框
        padding=(5, 2)
    )
    style.map('TButton',
        background=[('active', '#D9D9D9'), ('pressed', '#CCCCCC')],
        relief=[('pressed', 'sunken')]
    )
    
    # 辅助按钮样式 - 浅蓝色（浏览...按钮）
    style.configure('Auxiliary.TButton',
        background='#E1EFFF',  # 浅蓝色背景
        foreground='#000000',  # 黑色文字
        borderwidth=1,
        relief='raised',  # 3D凸起效果
        padding=(5, 2)
    )
    style.map('Auxiliary.TButton',
        background=[('active', '#D0E5FF'), ('pressed', '#BFDBFF')],
        relief=[('pressed', 'sunken')]
    )
    
    # 主要操作按钮样式 - 蓝色（执行按钮）- Material蓝色
    style.configure('Primary.TButton',
        background='#1976D2',  # Material Design 蓝色
        foreground='white',
        font=('Arial', 9, 'bold'),
        padding=(10, 5),
        relief='raised',  # 3D凸起效果
        borderwidth=2
    )
    style.map('Primary.TButton',
        background=[('active', '#1565C0'), ('pressed', '#0D47A1')],  # 加深15%
        relief=[('pressed', 'sunken')]
    )
    
    # 标签按钮样式 - 用于顶部标签栏
    style.configure('Tab.TButton', 
        background='#F5F5F5',  # 未选中时浅灰色背景 - Material灰色50
        foreground='#212121',  # Material灰色900
        font=('Arial', 9),
        padding=(10, 5),
        relief='flat',
        borderwidth=1
    )
    style.map('Tab.TButton',
        background=[('active', '#E0E0E0'), ('pressed', '#BDBDBD')],  # Material灰色200/300
        foreground=[('active', '#000000')],
        relief=[('pressed', 'flat')]
    )
    
    # 选中状态的标签按钮样式 - 使用独立样式而非派生样式
    style.configure('TabSelected.TButton', 
        background='#1976D2',  # Material Design 蓝色500
        foreground='white',    # 白色文字
        font=('Arial', 9, 'bold'),  # 加粗字体
        padding=(10, 5),
        relief='flat',
        borderwidth=1
    )
    style.map('TabSelected.TButton',
        background=[('active', '#1565C0')],  # Material蓝色700
        relief=[('pressed', 'flat')]
    )
    
    # 次要按钮样式 - 灰色（预览按钮）
    style.configure('Secondary.TButton',
        background='#757575',  # Material灰色600
        foreground='white',
        font=('Arial', 9),
        padding=(10, 5),
        relief='raised',  # 3D凸起效果
        borderwidth=2
    )
    style.map('Secondary.TButton',
        background=[('active', '#616161'), ('pressed', '#424242')],  # Material灰色700/800
        relief=[('pressed', 'sunken')]
    )
    
    # 底部操作栏框架样式
    style.configure('ActionBar.TFrame', 
        background='#F5F5F5',  # Material灰色50
        relief='solid',
        borderwidth=1
    )
    
    # 输入框样式
    style.configure('TEntry',
        padding=2,
        fieldbackground='white',
        borderwidth=1,
        relief='solid'  # 更明显的边框
    )
    
    # 组合框样式
    style.configure('TCombobox',
        padding=2,
        fieldbackground='white',
        borderwidth=1
    )
    
    # 表格样式
    style.configure('Treeview',
        background='white',
        fieldbackground='white'
    )
    style.map('Treeview',
        background=[('selected', '#1976D2')],  # Material蓝色500
        foreground=[('selected', 'white')]
    )
    
    # 标签页样式
    style.configure('TNotebook', 
        background='#f5f5f5',  # 保留灰色背景作为边框
        tabposition='n',
        tabmargins=[0, 0, 0, 0]  # 消除标签页的边距
    )
    style.configure('TNotebook.Tab',
        background='#f5f5f5',
        padding=(10, 4),
        width=15  # 固定标签宽度，防止自动分配空间
    )
    style.map('TNotebook.Tab',
        background=[('selected', '#1976D2')],  # Material蓝色500
        foreground=[('selected', 'white')],
        expand=[('selected', [1, 1, 1, 0])]
    )
    
    # 确保标签页从左侧开始排列，而不是居中
    try:
        style.layout('TNotebook.Tab', [
            ('Notebook.tab', {
                'sticky': 'nswe',
                'children': [
                    ('Notebook.padding', {
                        'side': 'top',
                        'sticky': 'nswe',
                        'children': [
                            ('Notebook.label', {'side': 'left', 'sticky': ''})
                        ]
                    })
                ]
            })
        ])
    except tk.TclError:
        # 某些Tk版本可能不支持此布局调整，这种情况下忽略错误
        pass
    
    # 复选框样式
    style.configure('TCheckbutton',
        background='#FFFFFF'  # 与内容区域保持一致
    )
    
    # 单选按钮样式
    style.configure('TRadiobutton',
        background='#FFFFFF'  # 与内容区域保持一致
    )
    
    # 分隔符样式
    style.configure('TSeparator',
        background='#BDBDBD'  # Material灰色400
    )
    
    # 进度条样式
    style.configure('TProgressbar',
        background='#1976D2',  # Material蓝色500
        troughcolor='#f5f5f5',
        borderwidth=0,
        thickness=10
    )
    
    return style

def setup_styles():
    """
    配置应用的样式，调用configure_styles函数
    
    Returns:
        ttk.Style: 配置好的样式对象
    """
    return configure_styles() 