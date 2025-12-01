@echo off
chcp 65001 >nul
echo ========================================
echo PowerKey 打包脚本
echo ========================================

REM 检查并关闭正在运行的 PowerKey.exe
tasklist /FI "IMAGENAME eq PowerKey.exe" 2>NUL | find /I /N "PowerKey.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo [警告] 检测到 PowerKey.exe 正在运行
    echo 正在尝试关闭程序...
    taskkill /F /IM PowerKey.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo 程序已关闭
)

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
  --add-data "%ICON_PATH%;." ^
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


