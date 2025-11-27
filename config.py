# -*- coding: utf-8 -*-
"""
PowerKey 配置文件
定义基础路径和常量
"""

import os

# 基础路径 - 快捷方式存放目录
BASE_PATH = os.path.join(os.environ['LOCALAPPDATA'], 'Power Keys')

# F键映射 (F1-F12)
F_KEYS = {f'f{i}': f'F{i}' for i in range(1, 13)}

# 支持的字母键 (a-z)
LETTER_KEYS = set('abcdefghijklmnopqrstuvwxyz')

# 支持的数字键 (0-9)
NUMBER_KEYS = set('0123456789')

# 所有支持的快捷方式触发键
TRIGGER_KEYS = LETTER_KEYS | NUMBER_KEYS

# 游戏模式切换热键
GAME_MODE_HOTKEY = 'win+esc'

# 通知显示时间（秒）
NOTIFICATION_DURATION = 3


