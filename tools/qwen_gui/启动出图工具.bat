@echo off
title Qwen-Image 出图工具
echo [1/2] 检查服务是否已在运行...
curl -s -m 2 http://127.0.0.1:8099/api/stats >nul 2>&1
if %errorlevel%==0 (
    echo 服务已在运行，打开页面...
    start http://127.0.0.1:8099
    exit /b
)
echo [2/2] 启动服务并打开页面...
cd /d D:\WorkBuddy\AI_Video\tools\qwen_gui
start "" python server.py --port 8099
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8099
