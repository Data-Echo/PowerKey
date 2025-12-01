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
    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path)
        except Exception:
            pass

    # 如果没有图标文件，创建一个简单的图标
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='#2196F3')
    dc = ImageDraw.Draw(image)

    # 绘制一个 "P" 字母（代表 PowerKey）
    dc.text((width//4, height//4), "P", fill='white')

    return image


class SystemTray:
    """系统托盘图标管理器"""

    def __init__(self, on_exit: Optional[Callable] = None):
        """
        初始化系统托盘

        Args:
            on_exit: 退出程序时的回调函数
        """
        self.on_exit = on_exit
        self.icon = None
        self.running = False
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
