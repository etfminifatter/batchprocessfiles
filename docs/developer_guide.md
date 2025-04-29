# 批量文件处理工具开发指南

## 1. 项目结构

```
project_root/
├── main.py              # 程序入口文件
├── ui/                  # 用户界面相关代码
│   ├── main_window.py   # 主窗口实现
│   ├── styles/          # 样式配置
│   │   └── tk_styles.py # Tkinter样式配置
│   └── tabs/            # 功能选项卡
│       ├── create_files_tab.py    # 批量创建文件选项卡
│       ├── create_dirs_tab.py     # 批量创建目录选项卡
│       ├── create_sheets_tab.py   # 批量创建工作表选项卡
│       ├── rename_tab.py          # 批量重命名选项卡
│       └── move_copy_tab.py       # 批量移动/复制选项卡
├── utils/               # 工具函数
│   ├── file_utils.py    # 文件操作工具
│   ├── excel_utils.py   # Excel操作工具
│   └── log_utils.py     # 日志工具
├── resources/           # 资源文件
│   └── icons/           # 图标文件
├── logs/                # 日志文件目录
├── docs/                # 文档
│   ├── user_manual.md   # 用户手册
│   └── developer_guide.md # 开发指南
├── tests/               # 测试代码
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明
```

## 2. 架构设计

### 2.1 模块划分

本项目采用MVC架构设计：
- **Model**：`utils`目录中的工具函数，负责核心业务逻辑和数据处理
- **View**：`ui`目录中的界面代码，负责用户界面展示
- **Controller**：各选项卡类，负责处理用户输入并调用相应的模型功能

### 2.2 文件结构与职责

- **main.py**：应用程序入口，负责初始化日志系统、加载样式和创建主窗口
- **main_window.py**：创建主窗口，包含菜单栏、标签页和状态栏
- **tabs/*.py**：各功能选项卡的实现
- **utils/*.py**：工具函数，提供核心功能实现
- **tk_styles.py**：定义和配置Tkinter样式

## 3. 核心模块API

### 3.1 file_utils.py

```python
def create_files(names, target_dir, file_type, content_template=None, naming_rule=None, start_value=1, step=1, digits=3):
    """
    批量创建文件
    
    Args:
        names: 文件名列表
        target_dir: 目标目录
        file_type: 文件类型（扩展名）
        content_template: 内容模板
        naming_rule: 命名规则
        start_value: 序号起始值
        step: 序号步长
        digits: 序号位数
        
    Returns:
        (bool, str): 成功状态和消息
    """
    pass
    
def create_dirs(names, target_dir, naming_rule=None, start_value=1, step=1, digits=3, enable_hierarchy=False, indent_spaces=4):
    """
    批量创建目录
    
    Args:
        names: 目录名列表
        target_dir: 目标目录
        naming_rule: 命名规则
        start_value: 序号起始值
        step: 序号步长
        digits: 序号位数
        enable_hierarchy: 是否启用层级结构
        indent_spaces: 缩进空格数
        
    Returns:
        (bool, str): 成功状态和消息
    """
    pass
    
def rename_files(files, target_dir, find_text, replace_text, case_sensitive=True, scope='name'):
    """
    批量重命名文件
    
    Args:
        files: 文件路径列表
        target_dir: 目标目录
        find_text: 查找文本
        replace_text: 替换文本
        case_sensitive: 是否区分大小写
        scope: 作用范围（'name'或'ext'）
        
    Returns:
        (bool, str): 成功状态和消息
    """
    pass
    
def move_copy_files(files, target_dir, operation='copy', conflict_action='skip', preserve_structure=True):
    """
    批量移动/复制文件
    
    Args:
        files: 文件路径列表
        target_dir: 目标目录
        operation: 操作类型（'move'或'copy'）
        conflict_action: 冲突处理方式（'skip'、'overwrite'或'rename'）
        preserve_structure: 是否保留目录结构
        
    Returns:
        (bool, str): 成功状态和消息
    """
    pass
```

### 3.2 excel_utils.py

```python
def create_sheets(workbook_path, sheet_names, title_row=None, header_row=None):
    """
    批量创建工作表
    
    Args:
        workbook_path: Excel文件路径
        sheet_names: 工作表名称列表
        title_row: 标题行内容
        header_row: 表头行内容
    """
    pass
    
def read_sheet_names(file_path):
    """
    从Excel文件读取工作表名称
    
    Args:
        file_path: Excel文件路径
    """
    pass
    
def read_column_data(file_path, sheet_name, column_index, has_header=True):
    """
    从Excel文件读取指定列的数据
    
    Args:
        file_path: Excel文件路径
        sheet_name: 工作表名称
        column_index: 列索引（从1开始）
        has_header: 是否包含表头
    """
    pass
```

### 3.3 log_utils.py

```python
def setup_logger(name, log_dir='logs', level=logging.DEBUG):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    pass
    
def log_exception(logger, e, context=None):
    """
    记录异常信息
    
    Args:
        logger: 日志记录器
        e: 异常对象
        context: 异常发生的上下文描述
    """
    pass
    
def log_system_info(logger):
    """
    记录系统信息
    
    Args:
        logger: 日志记录器
    """
    pass
```

## 4. UI设计

### 4.1 布局结构

- **主窗口**：采用垂直布局
  - 顶部：菜单栏
  - 中间：选项卡区域
  - 底部：状态栏

- **选项卡内布局**：通常由上至下分为
  - 输入区域
  - 设置区域
  - 输出设置
  - 预览区域
  - 操作按钮

### 4.2 样式指南

- **颜色方案**：
  - 背景色：#f5f5f5（浅灰）
  - 主按钮：#0078D7（蓝色）
  - 次要按钮：#2196F3（浅蓝）
  - 表格选中行：#0078D7（蓝色）
  - 文本颜色：#333333（深灰）

- **组件样式**：
  - 按钮：圆角4px，内边距5px 2px
  - 输入框：内边距2px
  - 标签页：内边距10px 4px

## 5. 扩展指南

### 5.1 添加新功能选项卡

1. 在`ui/tabs/`目录下创建新的选项卡类，继承自`ttk.Frame`
2. 实现`__init__`和`setup_ui`方法
3. 实现`preview`和`execute`方法处理功能逻辑
4. 在`main_window.py`中导入新选项卡并添加到Notebook中

### 5.2 添加新工具函数

1. 根据功能性质，在`utils/`目录下选择合适的文件添加函数
2. 或创建新的工具文件，实现相关功能
3. 确保添加适当的日志记录和错误处理
4. 在相应的选项卡类中导入并使用该函数

### 5.3 修改样式

1. 在`ui/styles/tk_styles.py`文件中修改样式配置
2. 遵循现有的命名约定和样式分组

## 6. 调试与测试

### 6.1 日志系统

- 日志文件位于`logs/`目录
- 日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 查看日志文件以排查问题

### 6.2 单元测试

- 在`tests/`目录下添加单元测试
- 遵循`test_*.py`命名约定
- 使用`unittest`框架编写测试用例

### 6.3 手动测试

- 确保每个功能在不同输入条件下都能正常工作
- 测试边界条件和错误情况
- 验证UI响应和用户交互

## 7. 发布流程

### 7.1 版本控制

- 使用语义化版本号（X.Y.Z）
  - X: 主版本号，不兼容的API变更
  - Y: 次版本号，向后兼容的功能性新增
  - Z: 修订号，向后兼容的问题修正

### 7.2 打包发布

1. 更新版本号
2. 更新`README.md`和文档
3. 使用PyInstaller创建可执行文件：
   ```
   pyinstaller --onefile --windowed --icon=resources/icons/logo.ico main.py
   ```
4. 测试打包后的应用
5. 创建发布包，包含可执行文件和必要的资源 