"""
文件管理模块

该模块提供文件和目录管理功能。
"""

import os
import shutil
from typing import List, Optional


def ensure_dir(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    列出目录中的文件

    Args:
        directory: 目录路径
        extension: 文件扩展名过滤，如果为None则列出所有文件

    Returns:
        List[str]: 文件路径列表
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if extension is None or filename.lower().endswith(extension.lower()):
                files.append(filepath)
    
    return files


def safe_filename(filename: str) -> str:
    """
    生成安全的文件名，移除不允许的字符

    Args:
        filename: 原始文件名

    Returns:
        str: 安全的文件名
    """
    # 替换不允许的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 限制长度
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        name = name[:max_length - len(ext)]
        filename = name + ext
    
    return filename


def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        bool: 是否成功复制
    """
    if not os.path.exists(src) or not os.path.isfile(src):
        return False
    
    if os.path.exists(dst) and not overwrite:
        return False
    
    # 确保目标目录存在
    dst_dir = os.path.dirname(dst)
    ensure_dir(dst_dir)
    
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def remove_file(filepath: str) -> bool:
    """
    删除文件

    Args:
        filepath: 文件路径

    Returns:
        bool: 是否成功删除
    """
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return False
    
    try:
        os.remove(filepath)
        return True
    except Exception:
        return False
