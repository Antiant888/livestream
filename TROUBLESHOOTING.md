# 故障排除指南

## 常见问题及解决方案

### 1. 无法访问 http://localhost:3000

#### 问题原因
- 前端服务未启动
- 端口被占用
- 依赖安装失败
- 配置错误

#### 解决步骤

**步骤1: 检查前端服务状态**
```bash
# 进入前端目录
cd frontend

# 检查Node.js版本
node --version
npm --version

# 如果版本过低，请升级Node.js到16+
```

**步骤2: 重新安装前端依赖**
```bash
cd frontend

# 清理缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rmdir /s /q node_modules
del package-lock.json

# 重新安装依赖
npm install
```

**步骤3: 手动启动前端服务**
```bash
cd frontend
npm run dev
```

**步骤4: 检查端口占用**
```bash
# 检查3000端口是否被占用
netstat -ano | findstr :3000

# 如果被占用，可以修改端口
# 编辑 frontend/vite.config.ts
# 将 port: 3000 改为其他端口，如 3001
```

### 2. 无法访问 http://localhost:8000

#### 问题原因
- 后端服务未启动
- Python环境问题
- 数据库连接失败
- 依赖安装失败

#### 解决步骤

**步骤1: 检查Python环境**
```bash
# 检查Python版本
python --version

# 检查pip
pip --version
```

**步骤2: 检查虚拟环境**
```bash
cd backend

# 创建虚拟环境（如果不存在）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip
```

**步骤3: 安装依赖**
```bash
# 使用国内镜像安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装Playwright
playwright install
```

**步骤4: 检查数据库连接**
```bash
# 检查PostgreSQL服务是否运行
# Windows: 服务管理器中查看 PostgreSQL 服务
# 或使用命令: pg_ctl status

# 测试数据库连接
python -c "import psycopg2; conn = psycopg2.connect('postgresql://username:password@localhost:5432/glonghui_analysis'); print('连接成功')"
```

**步骤5: 手动启动后端**
```bash
cd backend
venv\Scripts\activate
python main.py
```

### 3. 依赖安装失败

#### Python依赖问题
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或使用阿里云镜像
pip install package_name -i https://mirrors.aliyun.com/pypi/simple/
```

#### Node.js依赖问题
```bash
# 清理npm缓存
npm cache clean --force

# 删除node_modules
rmdir /s /q node_modules

# 重新安装
npm install

# 如果仍然失败，尝试使用yarn
npm install -g yarn
yarn install
```

### 4. 数据库问题

#### 创建数据库
```sql
-- 使用psql命令行工具
psql -U postgres

-- 创建数据库
CREATE DATABASE glonghui_analysis;

-- 创建用户（可选）
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE glonghui_analysis TO username;
```

#### 配置环境变量
```bash
# 在backend目录下创建.env文件
echo DATABASE_URL=postgresql://username:password@localhost:5432/glonghui_analysis > .env
```

### 5. 端口占用问题

#### 检查端口占用
```bash
# 检查8000端口
netstat -ano | findstr :8000

# 检查3000端口
netstat -ano | findstr :3000

# 查找占用端口的进程
tasklist | findstr PID
```

#### 杀死占用进程
```bash
# 杀死占用8000端口的进程（替换PID为实际进程ID）
taskkill /PID PID /F

# 杀死占用3000端口的进程
taskkill /PID PID /F
```

### 6. 快速修复脚本

创建一个修复脚本 `fix_issues.bat`：

```batch
@echo off
echo ==========================================
echo 格隆汇系统问题修复脚本
echo ==========================================

echo 1. 检查环境...
python --version
node --version
npm --version

echo 2. 修复后端...
cd backend

if exist venv (
    echo 激活虚拟环境...
    call venv\Scripts\activate
) else (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate
)

echo 升级pip...
python -m pip install --upgrade pip

echo 安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo 安装Playwright...
playwright install

echo 3. 修复前端...
cd ..\frontend

echo 清理缓存...
npm cache clean --force

if exist node_modules (
    echo 删除旧的node_modules...
    rmdir /s /q node_modules
)

if exist package-lock.json (
    echo 删除package-lock.json...
    del package-lock.json
)

echo 重新安装前端依赖...
npm install

echo 4. 启动服务...
echo 后端服务将在新窗口启动...
start "后端服务" cmd /k "cd backend && venv\Scripts\activate && python main.py"

echo 前端服务将在3秒后启动...
timeout /t 3 /nobreak >nul
start "前端界面" cmd /k "cd frontend && npm run dev"

echo ==========================================
echo 修复完成！请访问：
echo - 后端API: http://localhost:8000
echo - 前端界面: http://localhost:3000
echo ==========================================

pause
```

### 7. 手动测试步骤

#### 测试后端API
```bash
# 测试后端是否正常运行
curl http://localhost:8000/

# 如果返回JSON，说明后端正常
# 如果连接失败，检查后端是否启动
```

#### 测试前端
```bash
# 进入frontend目录
cd frontend

# 检查package.json中的scripts
# 确认有 "dev": "vite" 这一项

# 手动启动
npm run dev

# 查看控制台输出，是否有错误信息
```

### 8. 替代方案

如果仍然无法启动，可以使用以下替代方案：

#### 方案1: 使用Docker（推荐）
```bash
# 创建docker-compose.yml文件
# 然后运行: docker-compose up
```

#### 方案2: 使用在线服务
- 将后端部署到云服务器
- 使用Vercel部署前端
- 使用云数据库服务

#### 方案3: 简化版本
- 只运行后端API
- 使用Postman测试API
- 使用简单的HTML页面展示数据

### 9. 获取帮助

如果以上方法都无法解决问题：

1. **查看错误日志**
   - 后端控制台输出
   - 前端控制台输出
   - 浏览器开发者工具Console

2. **检查系统环境**
   - Windows版本
   - Python版本
   - Node.js版本
   - 网络连接状态

3. **联系技术支持**
   - 提供详细的错误信息
   - 提供系统环境信息
   - 提供操作步骤

## 快速检查清单

- [ ] Python 3.9+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] PostgreSQL 正在运行
- [ ] 数据库 glonghui_analysis 已创建
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] 端口8000和3000未被占用
- [ ] 虚拟环境已激活
- [ ] 环境变量已配置

## 紧急修复

如果时间紧迫，可以：

1. **只启动后端API**
   ```bash
   cd backend
   venv\Scripts\activate
   python main.py
   ```

2. **使用Postman测试API**
   - 访问 http://localhost:8000/docs
   - 使用Swagger UI测试接口

3. **生成模拟数据**
   ```bash
   curl -X POST http://localhost:8000/api/scrape/mock
   curl -X POST http://localhost:8000/api/analyze
   ```

4. **查看数据库内容**
   - 使用pgAdmin或psql查看数据
   - 验证数据是否正确存储