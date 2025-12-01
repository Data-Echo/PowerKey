# -*- coding: utf-8 -*-
"""
开机自启动管理
通过 Windows 注册表实现开机自启动
"""

import os
import sys
import winreg


# 注册表路径
REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "PowerKey"


def get_executable_path() -> str:
    """
    获取可执行文件路径

    Returns:
        可执行文件的完整路径
    """
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        return sys.executable
    else:
        # 开发环境，返回 Python 脚本路径
        script_path = os.path.abspath(sys.argv[0])
        python_exe = sys.executable
        return f'"{python_exe}" "{script_path}"'


def is_startup_enabled() -> bool:
    """
    检查是否已启用开机自启动

    Returns:
        True 表示已启用，False 表示未启用
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            # 检查路径是否匹配当前程序
            current_path = get_executable_path()
            return current_path.lower() in value.lower()
        except WindowsError:
            winreg.CloseKey(key)
            return False
    except WindowsError:
        return False


def enable_startup() -> bool:
    """
    启用开机自启动

    Returns:
        True 表示成功，False 表示失败
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_WRITE
        )
        executable_path = get_executable_path()
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, executable_path)
        winreg.CloseKey(key)
        print(f"已启用开机自启动: {executable_path}")
        return True
    except Exception as e:
        print(f"启用开机自启动失败: {e}")
        return False


def disable_startup() -> bool:
    """
    禁用开机自启动

    Returns:
        True 表示成功，False 表示失败
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_WRITE
        )
        try:
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
            print("已禁用开机自启动")
            return True
        except WindowsError:
            # 项不存在，认为是成功
            winreg.CloseKey(key)
            return True
    except Exception as e:
        print(f"禁用开机自启动失败: {e}")
        return False
