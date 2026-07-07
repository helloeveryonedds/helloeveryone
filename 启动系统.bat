@echo off
<<<<<<< HEAD
chcp 65001 >nul
cd /d "%~dp0"
title 房价预测系统 v2.0

echo ============================================================
echo    房价预测系统 v2.0
echo    启动流程: 爬取 → 加权重训 → 启动服务
echo    新数据权重为旧数据3倍，预测更贴近当前市场
echo ============================================================
=======
cd /d "%~dp0"
title House Price Prediction System

echo ================================================
echo    House Price Prediction System v2.0
echo    Support: Guangzhou / Shanghai
echo ================================================
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
<<<<<<< HEAD
    echo [错误] 未检测到 Python，请安装 Python 3.9+
=======
    echo [ERROR] Python not found. Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    pause
    exit /b
)

:: Install dependencies
<<<<<<< HEAD
echo [1/4] 安装依赖...
python -m pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    python -m pip install -r requirements.txt -q
)
echo        检测 Playwright 浏览器...
python -c "from playwright.sync_api import sync_playwright; print('OK')" 2>nul || (
    echo        首次安装 Playwright 浏览器内核...
    python -m playwright install chromium
)
echo       完成

:: 爬取 + 加权重训（5页约150条，新数据权重3倍）
echo [2/4] 爬取最新数据 + 加权重训模型...
:: 有头浏览器可见，第一次需手动解验证码，之后Cookie会保存
set BROWSER_DATA=%CD%\browser_cache
if not exist "%BROWSER_DATA%" mkdir "%BROWSER_DATA%"
python retrain.py --crawl-pages 5 --weight 3 --user-data-dir "%BROWSER_DATA%"
echo.

:: 启动 Flask 服务（加载新模型）
echo [3/4] 启动预测服务...
echo.
echo ============================================================
echo   访问: http://127.0.0.1:5000
echo   新模型已加载，预测基于最新市场数据
echo   如需完整重训: python retrain.py --crawl-pages 30
echo   按 Ctrl+C 停止
echo ============================================================
=======
echo [1/3] Installing dependencies...
python -m pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [WARN] Primary mirror failed, trying default...
    python -m pip install -r requirements.txt -q
)
echo       Done

:: Start server
echo [2/3] Starting Flask server...
echo.
echo ================================================
echo   Open browser to: http://127.0.0.1:5000
echo   Press Ctrl+C to stop
echo ================================================
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
echo.

cd /d "%~dp0app"
set PYTHONUTF8=1
python server.py

pause
