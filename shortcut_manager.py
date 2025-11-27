# -*- coding: utf-8 -*-
"""
PowerKey 快捷方式管理模块
处理文件夹创建和快捷方式启动
"""

import os
import subprocess
from config import BASE_PATH


def get_folder_path(f_key: str) -> str:
    """
    获取指定F键对应的文件夹路径
    
    Args:
        f_key: F键名称，如 'F1', 'F2' 等
    
    Returns:
        文件夹完整路径
    """
    return os.path.join(BASE_PATH, f_key)


def ensure_folder_exists(f_key: str) -> str:
    """
    确保F键对应的文件夹存在，不存在则创建
    
    Args:
        f_key: F键名称，如 'F1', 'F2' 等
    
    Returns:
        文件夹完整路径
    """
    folder_path = get_folder_path(f_key)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def open_folder(f_key: str) -> bool:
    """
    打开F键对应的文件夹（在资源管理器中）
    
    Args:
        f_key: F键名称，如 'F1', 'F2' 等
    
    Returns:
        是否成功打开
    """
    try:
        folder_path = ensure_folder_exists(f_key)
        os.startfile(folder_path)
        return True
    except Exception as e:
        print(f"打开文件夹失败: {e}")
        return False


def find_shortcut(f_key: str, letter: str) -> str | None:
    """
    在F键文件夹中查找以指定字母命名的快捷方式
    
    Args:
        f_key: F键名称，如 'F1', 'F2' 等
        letter: 字母键，如 'a', 'b' 等
    
    Returns:
        快捷方式完整路径，未找到返回 None
    """
    folder_path = get_folder_path(f_key)
    
    if not os.path.exists(folder_path):
        return None
    
    # 支持的快捷方式扩展名
    extensions = ['.lnk', '.url', '']
    
    for ext in extensions:
        # 尝试小写和大写字母
        for name in [letter.lower(), letter.upper()]:
            shortcut_path = os.path.join(folder_path, name + ext)
            if os.path.exists(shortcut_path):
                return shortcut_path
    
    return None


def launch_shortcut(f_key: str, letter: str) -> bool:
    """
    启动指定的快捷方式
    
    Args:
        f_key: F键名称，如 'F1', 'F2' 等
        letter: 字母键，如 'a', 'b' 等
    
    Returns:
        是否成功启动
    """
    shortcut_path = find_shortcut(f_key, letter)
    
    if shortcut_path is None:
        return False
    
    try:
        os.startfile(shortcut_path)
        return True
    except Exception as e:
        print(f"启动快捷方式失败: {e}")
        return False


def init_base_folder():
    """
    初始化基础文件夹
    """
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)


