from functools import partial
import time
import keyboard
from typing import Callable, Dict, List, Optional
from config import F_KEYS, TRIGGER_KEYS, GAME_MODE_HOTKEY, COMMON_F_KEYS

# 需要放行的修饰键（按住这些键时不阻拦 F 键）
MODIFIER_KEYS = [
    'ctrl',
    'left ctrl',
    'right ctrl',
    'alt',
    'left alt',
    'right alt',
    'shift',
    'left shift',
    'right shift',
]

WINDOWS_KEYS = ['win', 'windows', 'left windows', 'right windows']

HOTKEY_PARTS = [part.strip().lower() for part in GAME_MODE_HOTKEY.split('+')]
if len(HOTKEY_PARTS) != 2:
    raise ValueError('GAME_MODE_HOTKEY 必须形如 "win+esc"')
GAME_MODE_MODIFIER_KEY, GAME_MODE_TRIGGER_KEY = HOTKEY_PARTS


class KeyboardHandler:
    """键盘事件处理器"""

    def __init__(self):
        # 游戏模式状态
        self.game_mode: bool = False
        self.last_toggle_time: float = 0.0

        # 回调函数
        self.on_open_folder: Optional[Callable[[str], None]] = None
        self.on_launch_shortcut: Optional[Callable[[str, str], None]] = None
        self.on_game_mode_toggle: Optional[Callable[[bool], None]] = None

        # hook/热键句柄
        self.f_key_handlers: Dict[str, Callable] = {}
        self.shortcut_hotkeys: List[int] = []
        self.toggle_hook = None

    def set_callbacks(
        self,
        on_open_folder: Callable[[str], None],
        on_launch_shortcut: Callable[[str, str], None],
        on_game_mode_toggle: Callable[[bool], None],
    ):
        """设置回调函数"""
        self.on_open_folder = on_open_folder
        self.on_launch_shortcut = on_launch_shortcut
        self.on_game_mode_toggle = on_game_mode_toggle

    # region 注册/注销

    def _register_f_key_hooks(self):
        """只为不常用的功能键注册拦截"""
        if self.f_key_handlers:
            return
        for key_name, f_key in F_KEYS.items():
            # 常用功能键直接放行，不注册拦截
            if key_name in COMMON_F_KEYS:
                continue
            handler = self._create_f_key_handler(key_name, f_key)
            self.f_key_handlers[key_name] = handler
            keyboard.hook_key(key_name, handler, suppress=True)

    def _unregister_f_key_hooks(self):
        for handler in self.f_key_handlers.values():
            try:
                keyboard.unhook(handler)
            except KeyError:
                pass
        self.f_key_handlers.clear()

    def _register_shortcut_hotkeys(self):
        """为所有功能键注册快捷键组合"""
        if self.shortcut_hotkeys:
            return
        for key_name, f_key in F_KEYS.items():
            # Fx + Enter
            enter_hotkey = keyboard.add_hotkey(
                f"{key_name}+enter",
                partial(self._handle_open_folder_combo, f_key),
                suppress=True,
                trigger_on_release=False,
            )
            self.shortcut_hotkeys.append(enter_hotkey)

            # Fx + 字母/数字
            for trigger in TRIGGER_KEYS:
                combo = keyboard.add_hotkey(
                    f"{key_name}+{trigger}",
                    partial(self._handle_shortcut_combo, f_key, trigger),
                    suppress=True,
                    trigger_on_release=False,
                )
                self.shortcut_hotkeys.append(combo)

    def _unregister_shortcut_hotkeys(self):
        for hotkey in self.shortcut_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except KeyError:
                pass
        self.shortcut_hotkeys.clear()

    # endregion

    def _register_toggle_hotkey(self):
        if self.toggle_hook is None:
            self.toggle_hook = keyboard.on_press_key(
                GAME_MODE_TRIGGER_KEY,
                self._handle_game_mode_trigger,
                suppress=False,
            )

    def _unregister_toggle_hotkey(self):
        if self.toggle_hook is not None:
            keyboard.unhook(self.toggle_hook)
            self.toggle_hook = None

    def _handle_game_mode_trigger(self, event):
        """处理游戏模式组合键"""
        if not self._required_modifier_pressed():
            return

        current = time.time()
        if current - self.last_toggle_time < 0.3:
            return
        self.last_toggle_time = current
        self._toggle_game_mode()

    def _handle_open_folder_combo(self, f_key: str):
        """处理 Fx + Enter"""
        if self.game_mode:
            return
        if self.on_open_folder:
            self.on_open_folder(f_key)

    def _handle_shortcut_combo(self, f_key: str, trigger: str):
        """处理 Fx + 字母/数字"""
        if self.game_mode:
            return
        if self.on_launch_shortcut:
            self.on_launch_shortcut(f_key, trigger)

    def _create_f_key_handler(self, key_name: str, f_key: str):
        """生成 F 键 hook 处理函数"""

        def handler(event):
            if self.game_mode:
                return
            if event.event_type == "down":
                self._handle_f_key_down(key_name)

        return handler

    def _handle_f_key_down(self, key_name: str):
        """处理 F 键按下 - 如果有修饰键则放行，否则拦截"""
        if self._modifier_active():
            self._pass_through_key(key_name)

    def _modifier_active(self) -> bool:
        """判断是否有修饰键被按住"""
        return any(keyboard.is_pressed(mod) for mod in (MODIFIER_KEYS + WINDOWS_KEYS))

    def _is_windows_pressed(self) -> bool:
        """是否按下了 Windows 键"""
        return any(keyboard.is_pressed(key) for key in WINDOWS_KEYS)

    def _required_modifier_pressed(self) -> bool:
        """判断游戏模式所需的修饰键是否按下"""
        if GAME_MODE_MODIFIER_KEY in ('win', 'windows'):
            return self._is_windows_pressed()
        return keyboard.is_pressed(GAME_MODE_MODIFIER_KEY)

    def _pass_through_key(self, key_name: str):
        """暂时放行 F 键（用于修饰键场景）"""
        handler = self.f_key_handlers.get(key_name)
        if handler is None:
            return
        keyboard.unhook(handler)
        try:
            keyboard.send(key_name)
        finally:
            keyboard.hook_key(key_name, handler, suppress=True)

    def _toggle_game_mode(self):
        """切换游戏模式"""
        self.game_mode = not self.game_mode
        if self.game_mode:
            self._unregister_f_key_hooks()
            self._unregister_shortcut_hotkeys()
        else:
            self._register_f_key_hooks()
            self._register_shortcut_hotkeys()

        if self.on_game_mode_toggle:
            self.on_game_mode_toggle(self.game_mode)

    def start(self):
        """开始监听键盘事件"""
        self._register_f_key_hooks()
        self._register_shortcut_hotkeys()
        self._register_toggle_hotkey()

    def stop(self):
        """停止监听键盘事件"""
        self._unregister_toggle_hotkey()
        self._unregister_shortcut_hotkeys()
        self._unregister_f_key_hooks()

