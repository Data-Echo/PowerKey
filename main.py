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
    显示 Windows 气泡通知
    
    Args:
        title: 通知标题
        message: 通知内容
    """
    try:
        # 使用 PowerShell 显示通知（更简单可靠）
        import subprocess
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
        <toast>
            <visual>
                <binding template="ToastText02">
                    <text id="1">{title}</text>
                    <text id="2">{message}</text>
                </binding>
            </visual>
        </toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("PowerKey").Show($toast)
        '''
        subprocess.Popen(
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
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """设置键盘事件回调"""
        self.keyboard_handler.set_callbacks(
            on_open_folder=self._on_open_folder,
            on_launch_shortcut=self._on_launch_shortcut,
            on_game_mode_toggle=self._on_game_mode_toggle
        )
    
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
        print("  双击 Fx       - 执行原有功能键效果")
        print("  Win + Esc     - 切换游戏模式")
        print()
        print("注意: 单次按下 Fx 会被阻拦，Fn+Fx 组合不受影响")
        print()
        print("按 Ctrl+C 退出程序")
        print("=" * 50)
        
        # 初始化基础文件夹
        init_base_folder()
        
        # 启动键盘监听
        self.keyboard_handler.start()
        
        # 显示启动通知
        show_notification("PowerKey", "程序已启动，按 Win+Esc 切换游戏模式")
        
        try:
            # 保持程序运行
            import keyboard
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n程序已退出")
        finally:
            self.keyboard_handler.stop()


def main():
    """程序入口"""
    app = PowerKey()
    app.run()


if __name__ == '__main__':
    main()


