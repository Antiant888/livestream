@echo off
echo ==========================================
echo 格隆汇直播流数据分析系统启动脚本
echo ==========================================

echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

echo 2. 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo 3. 检查PostgreSQL...
echo 请确保PostgreSQL已安装并运行在默认端口5432
echo 如果未安装，请先安装PostgreSQL并创建数据库: glonghui_analysis
pause

echo 4. 设置后端环境...
cd backend

if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate

echo 安装Python依赖...
pip install -r requirements.txt

echo 安装Playwright浏览器...
playwright install

echo 5. 设置前端环境...
cd ..\frontend

echo 安装前端依赖...
npm install

echo 6. 启动系统...
echo ==========================================
echo 系统启动说明:
echo - 后端API将运行在: http://localhost:8000
echo - 前端界面将运行在: http://localhost:3000
echo - 数据库: PostgreSQL (请确保已创建 glonghui_analysis 数据库)
echo ==========================================

echo 7. 启动后端服务...
start "后端服务" cmd /k "cd backend && venv\Scripts\activate && python main.py"

echo 8. 启动前端服务...
timeout /t 3 /nobreak >nul
start "前端界面" cmd /k "cd frontend && npm run dev"

echo ==========================================
echo 系统启动完成！
echo ==========================================
echo 使用说明:
echo 1. 等待后端和前端都启动完成
echo 2. 打开浏览器访问: http://localhost:3000
echo 3. 在仪表板中点击"刷新数据"按钮
echo 4. 或者使用以下命令生成模拟数据:
echo    curl -X POST http://localhost:8000/api/scrape/mock
echo    curl -X POST http://localhost:8000/api/analyze
echo ==========================================

pause