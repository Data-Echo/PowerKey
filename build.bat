@echo off
chcp 65001 >nul
echo ========================================
echo PowerKey 打包脚本
echo ========================================

echo.
echo 正在安装依赖...
pip install -r requirements.txt

set ICON_PATH=%~dp0icons.ico
if not exist "%ICON_PATH%" (
  echo [错误] 未找到图标文件: %ICON_PATH%
  goto end
)

echo.
echo 正在打包...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name PowerKey ^
  --icon="%ICON_PATH%" ^
  --distpath . ^
  --workpath build ^
  --specpath build ^
  --clean ^
  main.py

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位于: %cd%\PowerKey.exe
echo ========================================
pause

:end


