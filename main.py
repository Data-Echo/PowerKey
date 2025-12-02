# -*- coding: utf-8 -*-
"""
PowerKey - 功能键快捷方式启动器
主程序入口
"""

import sys
import ctypes
from ctypes import wintypes

from keyboard_handler import KeyboardHandler
from shortcut_manager import init_base_folder, open_folder, launch_shortcut
from system_tray import SystemTray
from config import BASE_PATH


# Windows API 常量
NIIF_INFO = 0x00000001
NIF_INFO = 0x00000010
NIF_ICON = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002


class NOTIFYICONDATA(ctypes.Structure):
    """Windows 通知图标数据结构"""
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
    ]


def show_notification(title: str, message: str):
    """
    显示 Windows 气泡通知（使用 plyer 库，不会显示 PowerShell 图标）

    Args:
        title: 通知标题
        message: 通知内容
    """
    try:
        # 使用 plyer 库显示通知（更轻量，不会显示额外的任务栏图标）
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name='PowerKey',
            timeout=2  # 2秒后自动消失
        )
    except Exception:
        # 如果 plyer 不可用，静默失败
        pass


class PowerKey:
    """PowerKey 主程序类"""

    def __init__(self):
        self.keyboard_handler = KeyboardHandler()
        self.system_tray = SystemTray(on_exit=self._on_exit, on_restart=self._on_restart)
        self._running = True
        self._setup_callbacks()

    def _setup_callbacks(self):
        """设置键盘事件回调"""
        self.keyboard_handler.set_callbacks(
            on_open_folder=self._on_open_folder,
            on_launch_shortcut=self._on_launch_shortcut,
            on_game_mode_toggle=self._on_game_mode_toggle,
            on_exit=self._on_exit,
            on_toggle_tray=self._on_toggle_tray
        )

    def _on_toggle_tray(self):
        """切换托盘图标显示/隐藏回调"""
        # 先记录当前状态
        was_visible = self.system_tray.visible

        # 切换显示状态
        self.system_tray.toggle_visibility()

        # 根据切换后的状态显示通知
        if was_visible:
            # 之前是显示的，现在隐藏了
            show_notification("PowerKey", "任务托盘已隐藏")
        else:
            # 之前是隐藏的，现在显示了
            show_notification("PowerKey", "任务托盘已显示")

    def _on_exit(self):
        """退出程序回调"""
        self._running = False
        show_notification("PowerKey", "程序正在退出...")
        self.keyboard_handler.stop()
        sys.exit(0)

    def _on_restart(self):
        """重启程序回调"""
        show_notification("PowerKey", "程序正在重启...")
        self.keyboard_handler.stop()
        self.system_tray.stop()

        # 获取当前可执行文件路径
        import os
        import subprocess

        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            executable = sys.executable
        else:
            # 开发环境，使用 Python 解释器重新运行
            executable = sys.executable
            script = os.path.abspath(__file__)
            # 启动新进程
            subprocess.Popen([executable, script])
            sys.exit(0)
            return

        # 启动新的程序实例
        subprocess.Popen([executable])
        sys.exit(0)

    def _on_open_folder(self, f_key: str):
        """
        打开文件夹回调
        
        Args:
            f_key: F键名称
        """
        if open_folder(f_key):
            print(f"已打开文件夹: {f_key}")
    
    def _on_launch_shortcut(self, f_key: str, letter: str):
        """
        启动快捷方式回调
        
        Args:
            f_key: F键名称
            letter: 字母键
        """
        if launch_shortcut(f_key, letter):
            print(f"已启动: {f_key} + {letter}")
        else:
            print(f"未找到快捷方式: {f_key}/{letter}")
    
    def _on_game_mode_toggle(self, is_game_mode: bool):
        """
        游戏模式切换回调
        
        Args:
            is_game_mode: 是否为游戏模式
        """
        if is_game_mode:
            print("已进入游戏模式")
            show_notification("PowerKey", "🎮 游戏模式已开启")
        else:
            print("已退出游戏模式")
            show_notification("PowerKey", "⌨️ 游戏模式已关闭")
    
    def run(self):
        """运行主程序"""
        print("=" * 50)
        print("PowerKey 功能键快捷方式启动器")
        print("=" * 50)
        print(f"快捷方式目录: {BASE_PATH}")
        print()
        print("使用方法:")
        print("  Fx + Enter    - 打开对应文件夹")
        print("  Fx + 字母/数字 - 启动对应快捷方式")
        print("  Win + Esc     - 切换游戏模式")
        print("  Win + F3      - 切换托盘图标显示/隐藏")
        print("  Win + F4      - 退出程序")
        print()
        print("常用功能键直接放行（F2重命名、F3搜索、F4关闭、F5刷新、F11全屏、F12控制台）")
        print("不常用功能键会被拦截用于启动快捷方式（F1/F6-F10）")
        print("注意: Fn+Fx 组合键不受影响")
        print()
        print("右键点击系统托盘图标可以退出程序、设置开机自启动或隐藏托盘")
        print("按 Ctrl+C 或 Win+F4 可退出程序")
        print("=" * 50)

        # 初始化基础文件夹
        init_base_folder()

        # 启动键盘监听
        self.keyboard_handler.start()

        # 启动系统托盘
        self.system_tray.start()

        # 显示启动通知
        show_notification("PowerKey", "程序已启动，按 Win+Esc 切换游戏模式")

        try:
            # 保持程序运行
            import time
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n程序已退出")
        finally:
            self.keyboard_handler.stop()
            self.system_tray.stop()


def main():
    """程序入口"""
    app = PowerKey()
    app.run()


if __name__ == '__main__':
    main()


