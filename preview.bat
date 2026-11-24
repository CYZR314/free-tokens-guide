@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   我的收藏夹 —— 本地预览
echo   地址： http://127.0.0.1:8124/home/
echo   关掉这个窗口就停止服务。
echo.
start "" http://127.0.0.1:8124/home/
py -3 -m http.server 8124 2>nul || python -m http.server 8124
pause