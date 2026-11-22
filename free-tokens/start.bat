@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PORT=8123"
echo.
echo   免费 Tokens 白嫖攻略 - 本地预览
echo   地址: http://127.0.0.1:%PORT%/
echo   关掉这个窗口即停止服务
echo.
start "" "http://127.0.0.1:%PORT%/"
py -3 -m http.server %PORT% 2>nul || python -m http.server %PORT%
echo.
echo   服务已停止。如果上面提示找不到命令，请先安装 Python，或用 VS Code 的 Live Server 插件。
pause