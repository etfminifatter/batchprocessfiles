import os
import logging
import traceback
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import platform
import psutil
import json
import shutil

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
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 获取当前日期
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'{name}_{current_date}.log')
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理器，则不再添加
    if logger.handlers:
        return logger
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 文件处理器（每日轮换）
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=7,  # 保留7天的日志
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # 记录系统信息
    log_system_info(logger)
    
    logger.info(f"日志系统初始化完成，级别: {logging.getLevelName(level)}, 日志文件: {log_file}")
    return logger

def log_exception(logger, e, context=None):
    """
    记录异常信息
    
    Args:
        logger: 日志记录器
        e: 异常对象
        context: 异常发生的上下文描述
    """
    error_message = str(e)
    stack_trace = traceback.format_exc()
    
    if context:
        logger.error(f"异常 [{context}]: {error_message}")
    else:
        logger.error(f"异常: {error_message}")
    
    logger.debug(f"堆栈跟踪: \n{stack_trace}")

def log_system_info(logger):
    """
    记录系统信息
    
    Args:
        logger: 日志记录器
    """
    try:
        # 获取当前驱动器
        current_drive = os.path.splitdrive(os.getcwd())[0]
        if not current_drive:
            current_drive = 'C:'  # 默认使用C盘
        
        # 获取系统信息
        system_info = {
            "操作系统": platform.platform(),
            "Python版本": platform.python_version(),
            "工作目录": os.getcwd(),
            "用户名": os.getlogin() if hasattr(os, 'getlogin') else 'Unknown',
            "程序路径": sys.executable,
            "处理器": platform.processor(),
            "节点名称": platform.node(),
            "Python位数": platform.architecture()[0]
        }
        
        # 获取内存信息
        try:
            virtual_memory = psutil.virtual_memory()
            system_info["总内存"] = f"{virtual_memory.total // (1024**2)}MB"
            system_info["可用内存"] = f"{virtual_memory.available // (1024**2)}MB"
            system_info["内存使用率"] = f"{virtual_memory.percent}%"
        except Exception as e:
            system_info["内存信息"] = f"获取失败: {str(e)}"
        
        # 获取磁盘信息
        try:
            disk_usage = psutil.disk_usage(current_drive)
            system_info["磁盘总空间"] = f"{disk_usage.total // (1024**3)}GB"
            system_info["磁盘可用空间"] = f"{disk_usage.free // (1024**3)}GB"
            system_info["磁盘使用率"] = f"{disk_usage.percent}%"
        except Exception as e:
            system_info["磁盘信息"] = f"获取失败: {str(e)}"
        
        # 获取CPU信息
        try:
            system_info["CPU使用率"] = f"{psutil.cpu_percent()}%"
            system_info["CPU核心数"] = psutil.cpu_count(logical=False)
            system_info["CPU逻辑核心数"] = psutil.cpu_count(logical=True)
        except Exception as e:
            system_info["CPU信息"] = f"获取失败: {str(e)}"
        
        # 记录系统信息
        logger.info(f"系统信息: {json.dumps(system_info, ensure_ascii=False, indent=2)}")
    except Exception as e:
        logger.error(f"记录系统信息失败: {str(e)}")

def log_operation_start(logger, operation_name, parameters=None):
    """
    记录操作开始
    
    Args:
        logger: 日志记录器
        operation_name: 操作名称
        parameters: 操作参数字典
    """
    message = f"开始操作: {operation_name}"
    if parameters:
        params_str = json.dumps(parameters, ensure_ascii=False)
        message += f", 参数: {params_str}"
    
    logger.info(message)

def log_operation_end(logger, operation_name, status="成功", success_count=0, fail_count=0, details=None):
    """
    记录操作结束
    
    Args:
        logger: 日志记录器
        operation_name: 操作名称
        status: 操作状态（"成功"或"失败"）
        success_count: 成功处理的项目数
        fail_count: 失败处理的项目数
        details: 操作详情字典
    """
    result_info = {
        "状态": status,
        "成功数": success_count,
        "失败数": fail_count
    }
    
    if details:
        result_info.update(details)
    
    message = f"结束操作: {operation_name}, {json.dumps(result_info, ensure_ascii=False)}"
    
    log_level = logging.INFO if status == "成功" else logging.ERROR
    logger.log(log_level, message)

def rotate_logs(log_dir='logs', max_days=7):
    """
    轮转日志文件，删除超过指定天数的日志
    
    Args:
        log_dir: 日志目录
        max_days: 最大保留天数
    """
    if not os.path.exists(log_dir):
        return
    
    # 当前时间
    current_time = datetime.now()
    
    # 遍历日志目录中的所有文件
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        
        # 检查是否是文件
        if os.path.isfile(file_path):
            # 获取文件修改时间
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 计算文件年龄（天数）
            file_age = (current_time - file_time).days
            
            # 如果文件超过指定天数，则删除
            if file_age > max_days:
                try:
                    os.remove(file_path)
                    print(f"已删除过期日志文件: {file_path}, 年龄: {file_age}天")
                except Exception as e:
                    print(f"删除日志文件失败: {file_path}, 错误: {str(e)}")

def log_validation_result(logger, field, value, is_valid, reason=None):
    """
    记录验证结果
    
    Args:
        logger: 日志记录器
        field: 字段名称
        value: 字段值
        is_valid: 是否有效
        reason: 无效原因
    """
    if is_valid:
        logger.debug(f"验证通过: {field}={value}")
    else:
        logger.warning(f"验证失败: {field}={value}, 原因: {reason}")

def log_file_operation(logger, operation_type, file_path, new_path=None, success=True, error=None):
    """
    记录文件操作
    
    Args:
        logger: 日志记录器
        operation_type: 操作类型（创建/删除/重命名/移动/复制）
        file_path: 文件路径
        new_path: 新文件路径（适用于重命名/移动/复制）
        success: 是否成功
        error: 错误信息（可选）
    """
    if success:
        if new_path:
            logger.info(f"{operation_type}文件: {file_path} -> {new_path}")
        else:
            logger.info(f"{operation_type}文件: {file_path}")
    else:
        if new_path:
            logger.error(f"{operation_type}文件失败: {file_path} -> {new_path}, 错误: {error}")
        else:
            logger.error(f"{operation_type}文件失败: {file_path}, 错误: {error}")

def setup_uncaught_exception_handler(logger):
    """
    设置未捕获异常的处理器
    
    Args:
        logger: 日志记录器
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # 键盘中断不记录堆栈，让默认处理程序处理
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 记录未捕获的异常
        logger.critical("未捕获异常:", exc_info=(exc_type, exc_value, exc_traceback))
        
    # 设置异常处理器
    sys.excepthook = handle_exception 

def clear_logs(log_dir='logs'):
    """
    清空日志目录中的所有日志文件
    
    Args:
        log_dir: 日志目录
    """
    if not os.path.exists(log_dir):
        return
    
    # 遍历日志目录中的所有文件
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        
        # 检查是否是文件
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"已删除日志文件: {file_path}")
            except Exception as e:
                print(f"删除日志文件失败: {file_path}, 错误: {str(e)}") 