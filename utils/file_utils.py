import os
import shutil
from datetime import datetime
import logging
from .log_utils import setup_logger, log_exception, log_operation_start, log_operation_end, log_file_operation
import re
import json
import csv
import openpyxl
import tkinter as tk
from tkinter import messagebox, simpledialog

# 创建文件工具模块的日志记录器
logger = setup_logger('file_utils', level=logging.DEBUG)

def create_files(names, target_dir, file_type=".txt", content_template=None, 
                naming_rule=None, start_value=1, step=1, digits=3):
    """
    批量创建文件
    
    参数:
    - names: 文件名列表
    - target_dir: 目标目录
    - file_type: 文件类型，如 .txt, .doc 等
    - content_template: 内容模板，可包含变量 ${NAME}, ${ISEQ}
    - naming_rule: 命名规则，例如 "prefix_$NAME_$ISEQ3"
    - start_value: 序号起始值
    - step: 序号步长
    - digits: 序号位数
    
    返回元组 (成功标志, 消息)
    """
    logger.info(f"开始创建文件，共{len(names)}个，目标目录：{target_dir}")
    
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            logger.info(f"目标目录不存在，已创建：{target_dir}")
        except Exception as e:
            error_msg = f"创建目标目录失败：{str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    if not os.path.isdir(target_dir):
        error_msg = f"目标路径不是目录：{target_dir}"
        logger.error(error_msg)
        return False, error_msg
    
    created_count = 0
    skipped_count = 0
    error_files = []
    
    for i, name in enumerate(names):
        if not name.strip():
            logger.warning(f"跳过空文件名，索引：{i+1}")
            continue
        
        seq = start_value + i * step
        seq_str = str(seq).zfill(digits)
        
        try:
            # 处理命名规则
            if naming_rule:
                filename = apply_naming_rule(naming_rule, name, seq)
            else:
                filename = name
            
            # 添加文件扩展名
            if not filename.endswith(file_type):
                filename += file_type
            
            file_path = os.path.join(target_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                logger.warning(f"文件已存在，跳过：{file_path}")
                skipped_count += 1
                continue
            
            # 创建文件并写入内容
            file_content = ""
            if content_template:
                # 替换内容模板中的变量
                file_content = content_template.replace("${NAME}", name)
                file_content = file_content.replace("${ISEQ}", seq_str)
            
            create_file_with_type(file_path, file_content, file_type)
            logger.info(f"创建文件成功：{file_path}")
            created_count += 1
            
        except Exception as e:
            error_msg = f"处理文件 {name} 时出错：{str(e)}"
            logger.error(error_msg)
            error_files.append(name)
    
    result_msg = f"创建完成。成功：{created_count}个，跳过：{skipped_count}个，失败：{len(error_files)}个"
    if error_files:
        result_msg += f"，失败文件：{', '.join(error_files[:5])}"
        if len(error_files) > 5:
            result_msg += f" 等{len(error_files)}个"
    
    logger.info(result_msg)
    return True, result_msg

def apply_naming_rule(rule, name, seq):
    """
    应用命名规则
    
    参数:
    - rule: 命名规则，例如 "prefix_$NAME_$ISEQ3"
    - name: 原始名称
    - seq: 序号
    
    返回生成的文件名
    """
    # 替换基本变量
    result = rule.replace('$NAME', name)
    
    # 处理序号变量，支持指定位数
    seq_matches = re.findall(r'\$ISEQ(\d*)', result)
    for seq_match in seq_matches:
        if seq_match:
            seq_digits = int(seq_match)
            seq_formatted = str(seq).zfill(seq_digits)
            result = result.replace(f'$ISEQ{seq_match}', seq_formatted)
        else:
            result = result.replace('$ISEQ', str(seq))
    
    # 处理日期变量
    now = datetime.now()
    result = result.replace('$YYYY', now.strftime('%Y'))
    result = result.replace('$MM', now.strftime('%m'))
    result = result.replace('$DD', now.strftime('%d'))
    
    return result

def create_file_with_type(file_path, content, file_type):
    """
    根据文件类型创建文件
    
    参数:
    - file_path: 文件路径
    - content: 文件内容
    - file_type: 文件类型 (.txt, .xlsx 等)
    """
    file_type = file_type.lower()
    
    if file_type in ['.txt', '.md', '.py', '.html', '.css', '.js', '.json', '.csv']:
        # 文本文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    elif file_type == '.xlsx':
        # Excel 文件
        wb = openpyxl.Workbook()
        ws = wb.active
        if content:
            # 如果有内容，按行写入
            for i, line in enumerate(content.split('\n')):
                ws.cell(row=i+1, column=1, value=line)
        wb.save(file_path)
    
    elif file_type == '.doc' or file_type == '.docx':
        try:
            from docx import Document
            doc = Document()
            if content:
                # 按段落添加内容
                for para in content.split('\n'):
                    if para.strip():
                        doc.add_paragraph(para)
            doc.save(file_path)
        except ImportError:
            # 如果没有python-docx，创建文本文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.warning(f"未安装python-docx库，已创建文本文件：{file_path}")
    
    else:
        # 默认创建空文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def create_dirs(dir_names, parent_dir, structure=None, naming_rule=None, 
               start_value=1, step=1, digits=3, enable_hierarchy=False, indent_spaces=4):
    """
    批量创建目录
    
    参数:
    - dir_names: 目录名称列表
    - parent_dir: 父目录
    - structure: 子目录结构 (可选)，例如 ["images", "docs", "src"]
    - naming_rule: 命名规则 (可选)
    - start_value: 序号起始值
    - step: 序号步长
    - digits: 序号位数
    - enable_hierarchy: 是否启用层级结构
    - indent_spaces: 缩进空格数
    
    返回元组 (成功标志, 消息)
    """
    logger.info(f"开始创建目录，共{len(dir_names)}个，父目录：{parent_dir}")
    
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir)
            logger.info(f"父目录不存在，已创建：{parent_dir}")
        except Exception as e:
            error_msg = f"创建父目录失败：{str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    if not os.path.isdir(parent_dir):
        error_msg = f"父路径不是目录：{parent_dir}"
        logger.error(error_msg)
        return False, error_msg
    
    created_count = 0
    skipped_count = 0
    error_dirs = []
    
    # 处理层级结构
    if enable_hierarchy:
        logger.info("启用层级结构处理，缩进空格数：" + str(indent_spaces))
        # 构建层级关系
        dir_tree = []
        current_path = parent_dir
        parent_at_level = {0: parent_dir}  # 记录每个层级的父目录路径
        
        for i, name in enumerate(dir_names):
            # 计算当前行的缩进层级
            original_name = name
            indent_count = 0
            while name.startswith(' '):
                name = name[1:]
                indent_count += 1
            
            # 计算层级
            level = indent_count // indent_spaces if indent_spaces > 0 else 0
            
            # 去除前导空格的目录名
            clean_name = name.strip()
            if not clean_name:
                logger.warning(f"跳过空目录名，索引：{i+1}")
                continue
            
            seq = start_value + i * step
            seq_str = str(seq).zfill(digits)
            
            try:
                # 处理命名规则
                if naming_rule:
                    dirname = apply_naming_rule(naming_rule, clean_name, seq)
                else:
                    dirname = clean_name
                
                # 确定父目录路径
                if level == 0:
                    # 顶层目录，父目录是parent_dir
                    parent_path = parent_dir
                elif level in parent_at_level:
                    # 使用该层级的父目录
                    parent_path = parent_at_level[level]
                else:
                    # 层级不连续，使用最近的上级层级作为父目录
                    found = False
                    for l in range(level-1, -1, -1):
                        if l in parent_at_level:
                            parent_path = parent_at_level[l]
                            found = True
                            logger.debug(f"找到不连续层级 {level} 的父目录: {parent_path} (层级 {l})")
                            break
                    
                    if not found:
                        parent_path = parent_dir
                        logger.warning(f"未找到层级 {level} 的父目录，使用根目录: {parent_dir}")
                
                # 创建完整路径
                dir_path = os.path.join(parent_path, dirname)
                
                # 检查目录是否已存在
                if os.path.exists(dir_path):
                    logger.warning(f"目录已存在，跳过：{dir_path}")
                    skipped_count += 1
                else:
                    # 创建目录
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"创建目录成功：{dir_path}（层级：{level}）")
                    created_count += 1
                
                # 记录当前目录为下一层级的父目录
                parent_at_level[level+1] = dir_path
                
                # 创建子目录结构（如果有）
                if structure:
                    for subdir in structure:
                        sub_path = os.path.join(dir_path, subdir)
                        if not os.path.exists(sub_path):
                            os.makedirs(sub_path, exist_ok=True)
                            logger.info(f"创建子目录成功：{sub_path}")
                
            except Exception as e:
                error_msg = f"处理目录 {original_name} 时出错：{str(e)}"
                logger.error(error_msg)
                error_dirs.append(original_name)
    else:
        # 不处理层级结构，直接创建目录
        for i, name in enumerate(dir_names):
            if not name.strip():
                logger.warning(f"跳过空目录名，索引：{i+1}")
                continue
            
            seq = start_value + i * step
            seq_str = str(seq).zfill(digits)
            
            try:
                # 处理命名规则
                if naming_rule:
                    dirname = apply_naming_rule(naming_rule, name, seq)
                else:
                    dirname = name
                
                dir_path = os.path.join(parent_dir, dirname)
                
                # 检查目录是否已存在
                if os.path.exists(dir_path):
                    logger.warning(f"目录已存在，跳过：{dir_path}")
                    skipped_count += 1
                    continue
                
                # 创建主目录
                os.makedirs(dir_path)
                
                # 创建子目录结构（如果有）
                if structure:
                    for subdir in structure:
                        os.makedirs(os.path.join(dir_path, subdir), exist_ok=True)
                
                logger.info(f"创建目录成功：{dir_path}")
                created_count += 1
                
            except Exception as e:
                error_msg = f"处理目录 {name} 时出错：{str(e)}"
                logger.error(error_msg)
                error_dirs.append(name)
    
    result_msg = f"创建完成。成功：{created_count}个，跳过：{skipped_count}个，失败：{len(error_dirs)}个"
    if error_dirs:
        result_msg += f"，失败目录：{', '.join(error_dirs[:5])}"
        if len(error_dirs) > 5:
            result_msg += f" 等{len(error_dirs)}个"
    
    logger.info(result_msg)
    return True, result_msg

def rename_files(file_paths, find_text, replace_text, case_sensitive=True, whole_word=False, use_regex=False, rename_scope="both"):
    """
    批量重命名文件或文件夹
    
    参数:
    - file_paths: 文件或文件夹路径列表
    - find_text: 要查找的文本
    - replace_text: 要替换的文本
    - case_sensitive: 是否区分大小写
    - whole_word: 是否全词匹配
    - use_regex: 是否使用正则表达式
    - rename_scope: 重命名范围，可选值："name_only"(仅文件名)，"ext_only"(仅扩展名，文件夹忽略此选项)，"both"(文件名和扩展名)
    
    返回:
    - 成功重命名的项目数量
    """
    logger = logging.getLogger("file_utils")
    logger.info(f"开始重命名操作，共{len(file_paths)}个项目")
    
    renamed_count = 0
    skipped_count = 0
    error_files = []
    
    name_mapping = {}  # 用于存储文件名映射 {原路径: 新名称}
    
    # 生成文件名映射
    for file_path in file_paths:
        if not os.path.exists(file_path):
            logger.warning(f"路径不存在，跳过：{file_path}")
            skipped_count += 1
            continue
        
        # 判断是文件还是文件夹
        is_dir = os.path.isdir(file_path)
        file_name = os.path.basename(file_path)
        new_name = file_name  # 默认不变
        
        if is_dir:
            # 处理文件夹名称（对文件夹忽略扩展名设置）
            if rename_scope == "ext_only":
                # 对于文件夹，如果只替换扩展名则跳过
                logger.debug(f"文件夹不支持仅替换扩展名，跳过：{file_path}")
                continue
            
            # 替换文件夹名称
            if not use_regex:
                if case_sensitive:
                    if whole_word:
                        import re
                        folder_pattern = r'\b' + re.escape(find_text) + r'\b'
                        new_name = re.sub(folder_pattern, replace_text, file_name)
                    else:
                        new_name = file_name.replace(find_text, replace_text)
                else:
                    if whole_word:
                        import re
                        folder_pattern = r'\b' + re.escape(find_text) + r'\b'
                        new_name = re.sub(folder_pattern, replace_text, file_name, flags=re.IGNORECASE)
                    else:
                        new_name = _replace_case_insensitive(file_name, find_text, replace_text)
            else:
                # 使用正则表达式
                import re
                flags = 0 if case_sensitive else re.IGNORECASE
                new_name = re.sub(find_text, replace_text, file_name, flags=flags)
        else:
            # 处理文件
            # 分离文件名和扩展名
            name_part, ext_part = os.path.splitext(file_name)
            
            # 根据应用范围确定要替换的部分
            if rename_scope == "name_only":
                # 只替换文件名部分
                if not use_regex:
                    if case_sensitive:
                        if whole_word:
                            # 全词匹配需要考虑边界
                            import re
                            name_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_name_part = re.sub(name_pattern, replace_text, name_part)
                        else:
                            new_name_part = name_part.replace(find_text, replace_text)
                    else:
                        if whole_word:
                            import re
                            name_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_name_part = re.sub(name_pattern, replace_text, name_part, flags=re.IGNORECASE)
                        else:
                            # 不区分大小写的替换
                            new_name_part = _replace_case_insensitive(name_part, find_text, replace_text)
                else:
                    # 使用正则表达式
                    import re
                    flags = 0 if case_sensitive else re.IGNORECASE
                    new_name_part = re.sub(find_text, replace_text, name_part, flags=flags)
                
                new_name = new_name_part + ext_part
            
            elif rename_scope == "ext_only":
                # 只替换扩展名部分（不包括点）
                ext_to_replace = ext_part[1:] if ext_part else ""
                
                if not use_regex:
                    if case_sensitive:
                        if whole_word:
                            import re
                            ext_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_ext = re.sub(ext_pattern, replace_text, ext_to_replace)
                        else:
                            new_ext = ext_to_replace.replace(find_text, replace_text)
                    else:
                        if whole_word:
                            import re
                            ext_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_ext = re.sub(ext_pattern, replace_text, ext_to_replace, flags=re.IGNORECASE)
                        else:
                            new_ext = _replace_case_insensitive(ext_to_replace, find_text, replace_text)
                else:
                    # 使用正则表达式
                    import re
                    flags = 0 if case_sensitive else re.IGNORECASE
                    new_ext = re.sub(find_text, replace_text, ext_to_replace, flags=flags)
                
                new_name = name_part + ("." + new_ext if new_ext else "")
            
            else:  # "both"
                # 替换整个文件名
                if not use_regex:
                    if case_sensitive:
                        if whole_word:
                            import re
                            filename_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_name = re.sub(filename_pattern, replace_text, file_name)
                        else:
                            new_name = file_name.replace(find_text, replace_text)
                    else:
                        if whole_word:
                            import re
                            filename_pattern = r'\b' + re.escape(find_text) + r'\b'
                            new_name = re.sub(filename_pattern, replace_text, file_name, flags=re.IGNORECASE)
                        else:
                            new_name = _replace_case_insensitive(file_name, find_text, replace_text)
                else:
                    # 使用正则表达式
                    import re
                    flags = 0 if case_sensitive else re.IGNORECASE
                    new_name = re.sub(find_text, replace_text, file_name, flags=flags)
        
        # 如果文件名发生了变化，则添加到映射中
        if new_name != file_name:
            name_mapping[file_path] = new_name
    
    # 执行重命名操作
    for file_path, new_name in name_mapping.items():
        file_dir = os.path.dirname(file_path)
        new_path = os.path.join(file_dir, new_name)
        
        try:
            # 检查新路径是否已存在且不是自身
            if os.path.exists(new_path) and os.path.normpath(new_path) != os.path.normpath(file_path):
                logger.warning(f"目标路径已存在，跳过：{new_path}")
                skipped_count += 1
                continue
            
            # 重命名文件或文件夹
            shutil.move(file_path, new_path)
            item_type = "文件夹" if os.path.isdir(new_path) else "文件"
            logger.info(f"重命名{item_type}成功：{file_path} -> {new_path}")
            renamed_count += 1
            
        except Exception as e:
            error_msg = f"处理路径 {file_path} 时出错：{str(e)}"
            logger.error(error_msg)
            error_files.append(file_path)
    
    result_msg = f"重命名完成。成功：{renamed_count}项，跳过：{skipped_count}项，失败：{len(error_files)}项"
    if error_files:
        result_msg += f"，失败项：{', '.join([os.path.basename(f) for f in error_files[:5]])}"
        if len(error_files) > 5:
            result_msg += f" 等{len(error_files)}个"
    
    logger.info(result_msg)
    return renamed_count

def _replace_case_insensitive(text, find, replace):
    """不区分大小写的文本替换"""
    index = 0
    result = ""
    find_lower = find.lower()
    text_lower = text.lower()
    
    while index < len(text):
        match_index = text_lower.find(find_lower, index)
        if match_index == -1:
            # 没有更多匹配
            result += text[index:]
            break
        
        # 添加匹配前的文本
        result += text[index:match_index]
        # 添加替换文本
        result += replace
        # 更新索引
        index = match_index + len(find)
    
    return result

def show_conflict_dialog(file_path, target_path):
    """
    显示文件冲突对话框
    
    参数:
    - file_path: 源文件路径
    - target_path: 目标文件路径
    
    返回:
    - 处理方式: "skip", "overwrite", "rename" 或 None (如果取消)
    - 是否对所有应用: True/False
    - 是否取消所有操作: True/False
    """
    try:
        # 尝试获取现有的Tk实例，如果存在
        try:
            root = tk.Tk()
            # 检查是否已存在其他Tk实例
            if tk._default_root is not None and tk._default_root != root:
                # 已存在其他Tk实例，关闭当前实例使用已有的
                root.destroy()
                root = tk.Toplevel(tk._default_root)
            else:
                # 没有其他Tk实例，使用当前创建的
                pass
        except Exception:
            # 如果获取现有实例出错，创建新的Toplevel
            try:
                root = tk.Toplevel()
            except Exception:
                # 最后尝试创建一个新的Tk实例
                root = tk.Tk()
        
        # 隐藏主窗口
        root.withdraw()
        
        # 格式化文件路径，限制长度
        max_path_length = 60
        short_src_path = file_path
        short_dst_path = target_path
        if len(short_src_path) > max_path_length:
            short_src_path = "..." + short_src_path[-(max_path_length-3):]
        if len(short_dst_path) > max_path_length:
            short_dst_path = "..." + short_dst_path[-(max_path_length-3):]
        
        # 获取文件信息
        src_size = os.path.getsize(file_path)
        src_mtime = os.path.getmtime(file_path)
        dst_size = os.path.getsize(target_path)
        dst_mtime = os.path.getmtime(target_path)
        
        # 格式化大小
        def format_size(size_in_bytes):
            if size_in_bytes < 1024:
                return f"{size_in_bytes} 字节"
            elif size_in_bytes < 1024 * 1024:
                return f"{size_in_bytes / 1024:.2f} KB"
            elif size_in_bytes < 1024 * 1024 * 1024:
                return f"{size_in_bytes / (1024 * 1024):.2f} MB"
            else:
                return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        # 格式化日期时间
        def format_time(timestamp):
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建简单对话框，不使用Toplevel
        dialog_result = {"choice": "skip", "apply_to_all": False, "cancel_all": False}
        
        # 使用messagebox替代自定义对话框
        msg = (
            f"文件冲突\n\n"
            f"源文件:\n"
            f"路径: {short_src_path}\n"
            f"大小: {format_size(src_size)}\n"
            f"修改时间: {format_time(src_mtime)}\n\n"
            f"目标文件 (已存在):\n"
            f"路径: {short_dst_path}\n"
            f"大小: {format_size(dst_size)}\n"
            f"修改时间: {format_time(dst_mtime)}\n\n"
            f"如何处理此冲突?"
        )
        
        # 创建一个简单的对话框
        options = ["跳过", "覆盖", "重命名", "对所有应用相同操作", "取消所有操作"]
        
        choice = simpledialog.askstring(
            "文件冲突", 
            msg + "\n\n选项：\n1 - 跳过\n2 - 覆盖\n3 - 重命名\n4 - 对所有冲突应用相同操作\n5 - 取消所有操作",
            initialvalue="1"
        )
        
        if choice is None:
            return "skip", False, True  # 用户关闭了对话框，取消所有操作
        
        try:
            choice_num = int(choice.strip())
            
            if choice_num == 1:
                return "skip", False, False
            elif choice_num == 2:
                return "overwrite", False, False
            elif choice_num == 3:
                return "rename", False, False
            elif choice_num == 4:
                # 用户选择对所有应用相同操作，再次询问使用哪个选项
                all_choice = simpledialog.askstring(
                    "对所有冲突应用", 
                    "选择对所有冲突应用的操作:\n1 - 跳过\n2 - 覆盖\n3 - 重命名",
                    initialvalue="1"
                )
                
                if all_choice is None:
                    return "skip", False, False
                
                all_choice_num = int(all_choice.strip())
                if all_choice_num == 1:
                    return "skip", True, False
                elif all_choice_num == 2:
                    return "overwrite", True, False
                elif all_choice_num == 3:
                    return "rename", True, False
                else:
                    return "skip", False, False
            elif choice_num == 5:
                return "skip", False, True  # 取消所有操作
            else:
                return "skip", False, False
        except (ValueError, TypeError):
            return "skip", False, False
            
    except Exception as e:
        logger.error(f"显示冲突对话框出错: {str(e)}")
        return "skip", False, False

def move_copy_files(files, target_dir, operation="copy", conflict_action="ask", preserve_structure=False):
    """
    批量移动或复制文件
    
    参数:
    - files: 文件路径列表
    - target_dir: 目标目录
    - operation: 操作类型，"move" 或 "copy"
    - conflict_action: 冲突处理方式，"ask"(询问), "overwrite"(覆盖), "skip"(跳过), "rename"(自动重命名)
    - preserve_structure: 是否保留文件夹结构
    
    返回元组 (成功数量, 失败数量)
    """
    log_operation_start(logger, f"{operation}文件", {
        "文件数量": len(files),
        "目标目录": target_dir,
        "冲突处理": conflict_action,
        "保留结构": preserve_structure
    })
    
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            logger.info(f"目标目录不存在，已创建：{target_dir}")
        except Exception as e:
            log_exception(logger, e, "创建目标目录")
            return 0, len(files)
    
    if not os.path.isdir(target_dir):
        logger.error(f"目标路径不是目录：{target_dir}")
        return 0, len(files)
    
    success_count = 0
    failed_count = 0
    
    # 查找所有文件的共同基础路径（如果需要保留结构）
    common_base = None
    if preserve_structure and len(files) > 1:
        common_base = os.path.commonpath([os.path.dirname(f) for f in files])
        logger.debug(f"找到共同基础路径: {common_base}")
    
    # 冲突处理的全局选择，用于保存用户的对所有冲突使用相同选择
    conflict_choice_for_all = None
    
    # 用户是否取消了整个操作
    operation_cancelled = False
    
    # 首先检查有多少个文件会冲突，如果数量过多可以提前警告用户
    if conflict_action == "ask":
        conflict_count = 0
        for file_path in files:
            if not os.path.exists(file_path):
                continue
            
            # 确定目标文件路径
            if preserve_structure and common_base:
                rel_path = os.path.relpath(os.path.dirname(file_path), common_base)
                target_subdir = os.path.join(target_dir, rel_path)
                target_path = os.path.join(target_subdir, os.path.basename(file_path))
            else:
                target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            # 检查是否存在冲突
            if os.path.exists(target_path):
                conflict_count += 1
        
        if conflict_count > 10:
            # 使用简单的消息框询问
            try:
                result = messagebox.askyesnocancel(
                    "文件冲突警告",
                    f"检测到 {conflict_count} 个文件将产生冲突，这可能会弹出多个询问对话框。\n\n"
                    f"是否为所有冲突应用相同的处理方式？\n\n"
                    f"• 是：设置一个全局处理方式\n"
                    f"• 否：单独处理每个冲突\n"
                    f"• 取消：取消整个操作",
                    icon=messagebox.WARNING
                )
                
                if result is None:  # 用户点击了取消
                    logger.info("用户取消了操作")
                    return 0, 0
                elif result:  # 用户点击了是
                    # 使用简单对话框询问用户选择
                    from tkinter import simpledialog
                    
                    choice = simpledialog.askstring(
                        "选择冲突处理方式", 
                        "请选择对所有冲突的处理方式:\n1 - 跳过\n2 - 覆盖\n3 - 重命名",
                        initialvalue="1"
                    )
                    
                    if choice is None:
                        logger.info("用户取消了操作")
                        return 0, 0
                    
                    try:
                        choice_num = int(choice.strip())
                        if choice_num == 1:
                            conflict_choice_for_all = "skip"
                        elif choice_num == 2:
                            conflict_choice_for_all = "overwrite"
                        elif choice_num == 3:
                            conflict_choice_for_all = "rename"
                        else:
                            conflict_choice_for_all = "skip"
                    except (ValueError, TypeError):
                        conflict_choice_for_all = "skip"
                    
                    logger.info(f"用户选择了对所有冲突使用相同的处理方式: {conflict_choice_for_all}")
            except Exception as e:
                # 如果对话框显示失败，记录错误并继续
                logger.error(f"显示冲突警告对话框出错: {str(e)}")
    
    for file_path in files:
        if operation_cancelled:
            logger.info("操作已被用户取消")
            break
            
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在，跳过：{file_path}")
            failed_count += 1
            continue
        
        try:
            # 确定目标文件路径
            if preserve_structure and common_base:
                # 计算相对路径
                rel_path = os.path.relpath(os.path.dirname(file_path), common_base)
                # 创建目标子目录
                target_subdir = os.path.join(target_dir, rel_path)
                if not os.path.exists(target_subdir):
                    os.makedirs(target_subdir)
                target_path = os.path.join(target_subdir, os.path.basename(file_path))
            else:
                target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            # 检查目标文件是否已存在
            if os.path.exists(target_path):
                if conflict_action == "skip":
                    logger.info(f"目标文件已存在，跳过：{target_path}")
                    continue
                elif conflict_action == "overwrite":
                    logger.info(f"目标文件已存在，将覆盖：{target_path}")
                elif conflict_action == "rename":
                    # 自动重命名，添加数字后缀
                    filename, ext = os.path.splitext(os.path.basename(file_path))
                    counter = 1
                    while os.path.exists(target_path):
                        new_filename = f"{filename}_{counter}{ext}"
                        target_path = os.path.join(os.path.dirname(target_path), new_filename)
                        counter += 1
                    logger.info(f"目标文件已存在，重命名为：{os.path.basename(target_path)}")
                elif conflict_action == "ask":
                    # 如果用户已经为所有冲突选择了相同的处理方式
                    if conflict_choice_for_all is not None:
                        user_choice = conflict_choice_for_all
                        apply_to_all = True
                        cancel_all = False
                    else:
                        # 显示冲突对话框
                        user_choice, apply_to_all, cancel_all = show_conflict_dialog(file_path, target_path)
                        
                        # 如果用户选择对所有应用相同操作
                        if apply_to_all:
                            conflict_choice_for_all = user_choice
                        
                        # 如果用户取消所有操作
                        if cancel_all:
                            operation_cancelled = True
                            logger.info("用户取消了所有操作")
                            break
                    
                    # 处理用户选择
                    if user_choice == "skip":
                        logger.info(f"用户选择跳过：{target_path}")
                        continue
                    elif user_choice == "overwrite":
                        logger.info(f"用户选择覆盖：{target_path}")
                    elif user_choice == "rename":
                        # 自动重命名，添加数字后缀
                        filename, ext = os.path.splitext(os.path.basename(file_path))
                        counter = 1
                        while os.path.exists(target_path):
                            new_filename = f"{filename}_{counter}{ext}"
                            target_path = os.path.join(os.path.dirname(target_path), new_filename)
                            counter += 1
                        logger.info(f"用户选择重命名：{os.path.basename(target_path)}")
            
            # 执行文件操作
            if operation == "move":
                shutil.move(file_path, target_path)
                log_file_operation(logger, "移动", file_path, target_path, True)
            else:  # copy
                shutil.copy2(file_path, target_path)
                log_file_operation(logger, "复制", file_path, target_path, True)
            
            success_count += 1
            
        except Exception as e:
            log_exception(logger, e, f"{operation}文件 {file_path}")
            log_file_operation(logger, operation, file_path, target_path if 'target_path' in locals() else None, False, str(e))
            failed_count += 1
    
    # 如果操作被取消，记录取消信息
    if operation_cancelled:
        operation_name = "移动" if operation == "move" else "复制"
        log_operation_end(logger, f"{operation_name}文件", "已取消", success_count, failed_count)
        return success_count, failed_count
    
    operation_name = "移动" if operation == "move" else "复制"
    log_operation_end(logger, f"{operation_name}文件", "成功" if failed_count == 0 else "部分成功", success_count, failed_count)
    
    return success_count, failed_count 