@echo off
REM GLM-OCR 快速启动脚本 (Windows)

echo.
echo =========================================
echo GLM-OCR 文档转换工具 - 快速启动
echo =========================================
echo.

REM 检查Python环境
echo 1. 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ 找到Python: %python_version%
echo.

REM 检查依赖
echo 2. 检查依赖...
if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    exit /b 1
)
echo ✓ 找到requirements.txt
echo.

REM 检查.env文件
echo 3. 配置检查...
if not exist ".env" (
    if exist ".env.example" (
        echo ❌ 缺少.env文件
        echo 请复制.env.example到.env并填入API密钥:
        echo   copy .env.example .env
        echo   编辑.env文件，填入ZHIPU_API_KEY
        exit /b 1
    )
)

REM 创建必要的目录
echo 4. 创建目录...
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
echo ✓ 目录检查完成
echo.

REM 启动应用
echo 5. 启动应用...
echo =========================================
echo 应用正在启动...
echo 请在浏览器中打开: http://localhost:7860
echo 按 Ctrl+C 停止应用
echo =========================================
echo.

python main.py
pause
