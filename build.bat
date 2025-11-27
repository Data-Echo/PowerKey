@echo off
chcp 65001 >nul
echo ========================================
echo PowerKey 打包脚本
echo ========================================

echo.
echo 正在安装依赖...
pip install -r requirements.txt

echo.
echo 正在打包...
pyinstaller --onefile --noconsole --name PowerKey --icon=icons.ico main.py

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位于: dist\PowerKey.exe
echo ========================================
pause


