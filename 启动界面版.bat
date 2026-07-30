@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动视频号下载器界面...
python "%~dp0gui\app.py"
if errorlevel 1 (
  echo.
  echo 启动失败：请先安装 Python 3.10+，并勾选 Add to PATH。
  pause
)
