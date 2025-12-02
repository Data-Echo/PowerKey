# -*- coding: utf-8 -*-
"""
系统托盘图标管理
提供退出程序和开机自启动功能
"""

import os
import sys
import threading
from typing import Callable, Optional
import pystray
from PIL import Image, ImageDraw
from startup_manager import is_startup_enabled, enable_startup, disable_startup


def create_icon_image():
    """创建托盘图标图像"""
    # 尝试加载自定义图标
    icon_path = os.path.join(os.path.dirname(__file__), 'icons.ico')

    # 如果是打包后的程序，图标路径需要调整
    if getattr(sys, 'frozen', False):
        # 打包后的程序，从 _MEIPASS 目录加载
        base_path = sys._MEIPASS
        icon_path = os.path.join(base_path, 'icons.ico')

    if os.path.exists(icon_path):
        try:
            # 加载 ICO 文件并提取合适的尺寸
            img = Image.open(icon_path)
            # ICO 文件包含多个尺寸，选择最合适的（通常是 32x32 或 16x16）
            # 确保图像是 RGBA 模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            return img
        except Exception as e:
            print(f"加载图标失败: {e}")

    # 如果没有图标文件，创建一个简单的图标
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (33, 150, 243, 255))  # 蓝色背景
    dc = ImageDraw.Draw(image)

    # 绘制一个 "PK" 字母（代表 PowerKey）
    # 使用更大的字体
    from PIL import ImageFont
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        # 如果没有找到字体，使用默认字体
        font = ImageFont.load_default()

    dc.text((8, 16), "PK", fill=(255, 255, 255, 255), font=font)

    return image


class SystemTray:
    """系统托盘图标管理器"""

    def __init__(self, on_exit: Optional[Callable] = None, on_restart: Optional[Callable] = None):
        """
        初始化系统托盘

        Args:
            on_exit: 退出程序时的回调函数
            on_restart: 重启程序时的回调函数
        """
        self.on_exit = on_exit
        self.on_restart = on_restart
        self.icon = None
        self.running = False
        self.visible = True  # 托盘是否可见
        self._thread = None

    def _create_menu(self):
        """创建托盘菜单"""
        startup_enabled = is_startup_enabled()

        return pystray.Menu(
            pystray.MenuItem(
                '开机自启动',
                self._toggle_startup,
                checked=lambda item: is_startup_enabled()
            ),
            pystray.MenuItem(
                '隐藏托盘',
                self._hide_tray
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                '退出程序',
                self._on_exit_clicked
            )
        )

    def _toggle_startup(self, icon, item):
        """切换开机自启动状态"""
        if is_startup_enabled():
            disable_startup()
        else:
            enable_startup()

        # 更新菜单
        icon.menu = self._create_menu()

    def _hide_tray(self, icon, item):
        """隐藏托盘图标"""
        self.visible = False
        self.stop()

    def toggle_visibility(self):
        """切换托盘图标显示/隐藏"""
        if self.visible:
            # 当前显示，隐藏它
            self.visible = False
            self.stop()
        else:
            # 当前隐藏，显示它
            self.visible = True
            self.start()

    def _on_left_click(self, icon, item):
        """处理左键点击 - 重启程序"""
        if self.on_restart:
            self.on_restart()

    def _on_exit_clicked(self, icon, item):
        """处理退出按钮点击"""
        self.stop()
        if self.on_exit:
            self.on_exit()

    def start(self):
        """启动系统托盘"""
        if self.running:
            return

        self.running = True

        # 创建图标
        image = create_icon_image()
        menu = self._create_menu()

        self.icon = pystray.Icon(
            name='PowerKey',
            icon=image,
            title='PowerKey - 功能键快捷启动器',
            menu=menu
        )

        # 设置左键单击事件
        self.icon.on_activate = self._on_left_click

        # 在单独的线程中运行托盘图标
        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()

    def _run_icon(self):
        """在线程中运行托盘图标"""
        try:
            self.icon.run()
        except Exception as e:
            print(f"系统托盘运行出错: {e}")

    def stop(self):
        """停止系统托盘"""
        if self.icon:
            self.icon.stop()
        self.running = False
