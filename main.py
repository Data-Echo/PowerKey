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

# 全局变量：用于终止上一个通知进程
_last_notification_process = None


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
    显示 Windows 气泡通知（快速版本，自动覆盖之前的通知）

    Args:
        title: 通知标题
        message: 通知内容
    """
    global _last_notification_process

    try:
        # 终止之前的通知进程
        if _last_notification_process is not None:
            try:
                _last_notification_process.terminate()
                _last_notification_process.wait(timeout=0.5)
            except:
                pass

        # 使用 PowerShell 显示通知，设置较短的显示时间
        import subprocess
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(1000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)
        Start-Sleep -Milliseconds 1500
        $notify.Dispose()
        '''

        _last_notification_process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        # 通知失败不影响主程序
        print(f"通知显示失败: {e}")


class PowerKey:
    """PowerKey 主程序类"""

    def __init__(self):
        self.keyboard_handler = KeyboardHandler()
        self.system_tray = SystemTray(on_exit=self._on_exit)
        self._running = True
        self._setup_callbacks()

    def _setup_callbacks(self):
        """设置键盘事件回调"""
        self.keyboard_handler.set_callbacks(
            on_open_folder=self._on_open_folder,
            on_launch_shortcut=self._on_launch_shortcut,
            on_game_mode_toggle=self._on_game_mode_toggle,
            on_exit=self._on_exit
        )

    def _on_exit(self):
        """退出程序回调"""
        self._running = False
        print("\n正在退出程序...")
        self.keyboard_handler.stop()
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
        print("  Win + F4      - 退出程序")
        print()
        print("常用功能键直接放行（F2重命名、F4关闭、F5刷新、F11全屏、F12控制台）")
        print("不常用功能键会被拦截用于启动快捷方式（F1/F3/F6-F10）")
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


