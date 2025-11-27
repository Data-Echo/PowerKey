# PowerKey

PowerKey 是一个基于 Windows 的功能键快捷启动工具，利用 F1-F12 组合键快速呼出指定文件夹、程序或快捷方式，提升键盘党效率。

## 主要特性

- **Fx + Enter**：打开 `C:\Users\<用户名>\AppData\Local\Power Keys\Fx` 对应目录（自动创建）。
- **Fx + 字母 / 数字**：执行该目录中同名的快捷方式或文件。
- **双击 Fx**：仍可触发原生功能键（如 F5 刷新、F1 帮助）。
- **Win + Esc**：切换游戏模式，暂停或恢复所有 PowerKey 功能，避免误触。
- **Fn + Fx 不受影响**：键盘固件级 Fn 逻辑原样生效。

## 使用方法

1. 克隆仓库并安装依赖：
   ```powershell
   git clone https://github.com/yourname/PowerKey.git
   cd PowerKey
   pip install -r requirements.txt
   ```
2. 运行：
   ```powershell
   python main.py
   ```
3. 可选：打包成独立可执行文件：
   ```powershell
   build.bat
   ```
   生成的 `dist\PowerKey.exe` 可直接在 Windows 上使用。

> ⚠️ 请以管理员权限运行，确保能够顺利监听全局键盘事件。

## 文件结构

```
PowerKey/
├── config.py            # 配置与常量
├── shortcut_manager.py  # 快捷方式/文件夹管理
├── keyboard_handler.py  # 键盘监听与组合键逻辑
├── main.py              # 程序入口
├── build.bat            # PyInstaller 打包脚本
└── requirements.txt     # 依赖清单
```

## 许可证 & 图标说明

- 代码以 MIT License 发布。
- 软件图标来自 [Icons8](https://icons8.com) 的 [Keyboard](https://icons8.com/icon/124063/keyboard) 图标，感谢其提供的开源资源。

欢迎提交 Issue 或 PR，一起完善 QuickKey！

