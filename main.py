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
    # 创建日志目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger()
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
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(name)s][%(filename)s:%(lineno)d] %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 记录启动信息
    logger.info("批量文件处理工具启动")
    
    # 设置未捕获异常处理器
    setup_uncaught_exception_handler(logger)
    
    return logger

def main():
    # 轮换日志文件
    rotate_logs()
    
    # 设置日志
    logger = setup_logger()
    
    try:
        # 尝试导入TkinterDnD
        try:
            import tkinterdnd2 as tkdnd
            # 如果成功导入，使用TkinterDnD的Tk类
            root = tkdnd.Tk()
            logger.info("成功初始化TkinterDnD，拖放功能已启用")
        except ImportError:
            # 如果未安装TkinterDnD，使用标准Tkinter
            root = tk.Tk()
            logger.warning("未能导入TkinterDnD，拖放功能已禁用")
        
        # 配置样式
        style = configure_styles()
        logger.info("应用样式配置完成")
        
        # 设置主窗口
        root.title("批量文件处理工具")
        root.geometry("960x680")  # 增加初始窗口尺寸
        root.minsize(960, 680)    # 设置最小窗口尺寸，防止窗口被缩小到界面变形
        
        # 设置应用图标
        if getattr(sys, 'frozen', False):
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
        
        # 创建主窗口实例
        app = MainWindow(root)
        
        # 启动主循环
        logger.info("启动主循环")
        root.mainloop()
    except Exception as e:
        logger.critical(f"应用启动失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 