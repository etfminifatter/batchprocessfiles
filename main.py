import tkinter as tk
from tkinter import ttk
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from ui.main_window import MainWindow
from ui.styles.tk_styles import configure_styles
from utils.log_utils import setup_uncaught_exception_handler, rotate_logs

def setup_logger():
    """设置全局日志记录器"""
    # 判断是否是打包版本
    is_frozen = getattr(sys, 'frozen', False)
    
    # 创建日志目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger()
    
    # 在打包版本中使用更高的日志级别
    if is_frozen:
        logger.setLevel(logging.ERROR)  # 仅保留ERROR级别，进一步减少日志处理
    else:
        logger.setLevel(logging.DEBUG)
    
    # 如果已经有处理器，则清除
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # 创建文件处理器（每日轮换）
    log_file = os.path.join(log_dir, 'batch_file_tool.log')
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    # 文件处理器级别
    if is_frozen:
        file_handler.setLevel(logging.ERROR)  # 打包版本只记录错误
    else:
        file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    # 在打包版本中控制台只显示错误
    if is_frozen:
        console_handler.setLevel(logging.CRITICAL)  # 只显示严重错误
    else:
        console_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器 - 打包版本使用更简单的格式
    if is_frozen:
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
    else:
        formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s][%(filename)s:%(lineno)d] %(message)s'
        )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 记录启动信息
    if is_frozen:
        logger.warning("批量文件处理工具启动(发布版)")
    else:
        logger.info("批量文件处理工具启动(开发版)")
    
    # 设置未捕获异常处理器
    setup_uncaught_exception_handler(logger)
    
    return logger

def main():
    # 判断是否是打包版本
    is_frozen = getattr(sys, 'frozen', False)
    
    # 只在开发版本中执行轮换日志
    if not is_frozen:
        rotate_logs()
    
    # 设置日志
    logger = setup_logger()
    
    try:
        # 创建根窗口 - 安全地尝试导入TkinterDnD，失败则使用标准Tkinter
        root = None
        dnd_available = False
        
        try:
            # 尝试以安全方式导入TkinterDnD
            import importlib
            tkdnd_spec = importlib.util.find_spec("tkinterdnd2")
            
            if tkdnd_spec is not None:
                try:
                    import tkinterdnd2
                    # 进一步验证tkdnd库是否可用
                    try:
                        root = tkinterdnd2.Tk()
                        # 尝试调用一个tkdnd特定的方法来验证它是否正常工作
                        root.TkdndVersion
                        dnd_available = True
                        logger.info("成功初始化TkinterDnD，拖放功能已启用")
                    except (AttributeError, RuntimeError, tk.TclError) as e:
                        logger.warning(f"TkinterDnD库加载失败: {str(e)}")
                        if root:
                            root.destroy()
                        root = None
                except ImportError as e:
                    logger.warning(f"导入TkinterDnD失败: {str(e)}")
        except Exception as e:
            logger.warning(f"尝试加载TkinterDnD时出错: {str(e)}")
        
        # 如果TkinterDnD初始化失败，使用标准Tkinter
        if root is None:
            root = tk.Tk()
            logger.warning("使用标准Tkinter，拖放功能已禁用")
        
        # 配置样式
        style = configure_styles()
        logger.info("应用样式配置完成")
        
        # 设置主窗口
        root.title("批量文件处理工具")
        root.geometry("960x680")  # 增加初始窗口尺寸
        root.minsize(960, 680)    # 设置最小窗口尺寸，防止窗口被缩小到界面变形
        
        # 设置应用图标
        if is_frozen:
            # 如果是打包后的exe
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(application_path, "resources", "icons", "logo.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
            logger.info(f"已设置应用图标: {icon_path}")
        else:
            logger.warning(f"应用图标不存在: {icon_path}")
        
        # 创建主窗口实例，并传递拖放可用性信息
        app = MainWindow(root, dnd_available=dnd_available)
        
        # 启动主循环
        logger.info("启动主循环")
        root.mainloop()
    except Exception as e:
        logger.critical(f"应用启动失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 