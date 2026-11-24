@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 上传到 GitHub + Cloudflare
echo ==========================================
echo   一键上传（改了 data.json 就跑这个）
echo ==========================================
echo.
python "%~dp0push.py"
if errorlevel 1 (
  echo.
  echo 试一下 py -3 ...
  py -3 "%~dp0push.py"
)
echo.
pause