@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo نصب پیش‌نیازهای JARVIS 3D...
py -m pip install --upgrade pip
if errorlevel 1 python -m pip install --upgrade pip
py -m pip install flask requests
if errorlevel 1 python -m pip install flask requests
echo.
echo اگر پیام خطا ندیدی، نصب تمام شده است.
pause
