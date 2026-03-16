# 部署指南

本指南将帮助您将格隆汇直播流数据分析系统部署到GitHub和Railway。

## 🚀 快速部署

### 1. 推送代码到GitHub

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库（替换your-username和your-repo）
git remote add origin https://github.com/your-username/your-repo.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 2. 在Railway上部署

#### 方法1: 通过GitHub集成（推荐）

1. **访问 [Railway](https://railway.app)**
2. **点击 "Deploy on Railway"**
3. **登录并授权GitHub账户**
4. **选择您的仓库**
5. **Railway会自动检测配置并部署**

#### 方法2: 手动创建项目

1. **登录Railway**
2. **点击 "New Project"**
3. **选择 "Deploy from GitHub repo"**
4. **选择您的仓库**
5. **配置环境变量**
6. **点击 "Deploy"**

### 3. 配置环境变量

在Railway仪表板中为您的项目配置以下环境变量：

#### Backend服务
```
DATABASE_URL=postgresql://username:password@hostname:port/database
PYTHON_VERSION=3.11
```

#### Frontend服务
```
VITE_API_URL=https://your-backend-url.railway.app
```

## 📋 手动部署步骤

### 步骤1: 准备GitHub仓库

1. **创建新的GitHub仓库**
   - 访问 [GitHub](https://github.com/new)
   - 创建新仓库
   - 复制仓库URL

2. **推送代码**
```bash
# 如果还没有初始化Git
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/your-username/your-repo.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤2: 配置Railway

1. **注册Railway账户**
   - 访问 [Railway](https://railway.app)
   - 使用GitHub登录

2. **连接GitHub仓库**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权GitHub访问
   - 选择您的仓库

3. **配置服务**
   - Railway会自动检测 `railway.json` 配置
   - 确认服务配置：
     - `backend`: Python服务
     - `frontend`: Node.js服务
     - `database`: PostgreSQL数据库

4. **设置环境变量**
   - 在Railway仪表板中设置必要的环境变量
   - 数据库连接会自动配置

5. **开始部署**
   - 点击 "Deploy" 按钮
   - 等待部署完成（通常需要5-10分钟）

### 步骤3: 验证部署

1. **检查服务状态**
   - 在Railway仪表板中查看服务状态
   - 确保所有服务都显示为 "Running"

2. **访问应用**
   - Backend API: `https://your-project-id.railway.app`
   - Frontend UI: `https://your-frontend-id.railway.app`

3. **测试功能**
   - 访问Swagger UI: `https://your-backend-id.railway.app/docs`
   - 生成模拟数据并查看结果

## 🔧 配置说明

### 环境变量

#### Backend服务
| 变量名 | 描述 | 示例 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL数据库连接字符串 | `postgresql://user:pass@host:port/db` |
| `PYTHON_VERSION` | Python版本 | `3.11` |

#### Frontend服务
| 变量名 | 描述 | 示例 |
|--------|------|------|
| `VITE_API_URL` | Backend API地址 | `https://backend-id.railway.app` |

### 服务配置

#### Backend (Python/FastAPI)
- **端口**: 8000
- **启动命令**: `python main.py`
- **健康检查**: `/`
- **依赖**: `requirements.txt`

#### Frontend (React/Vite)
- **端口**: 80
- **启动命令**: `npm run build && npm run preview`
- **健康检查**: `/`
- **依赖**: `package.json`

#### Database (PostgreSQL)
- **类型**: PostgreSQL
- **数据库名**: `glonghui_analysis`
- **自动配置**: 是

## 🐳 Docker部署

### 本地Docker部署

```bash
# 构建后端镜像
cd backend
docker build -t glonghui-backend .

# 构建前端镜像
cd frontend
docker build -t glonghui-frontend .

# 运行后端服务
docker run -d --name backend -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:port/db \
  glonghui-backend

# 运行前端服务
docker run -d --name frontend -p 3000:80 \
  -e VITE_API_URL=http://localhost:8000 \
  --link backend \
  glonghui-frontend
```

### Docker Compose部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@database:5432/glonghui_analysis
    depends_on:
      - database
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=glonghui_analysis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

运行：
```bash
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

#### 1. 部署失败
- **检查日志**: 在Railway仪表板中查看部署日志
- **依赖问题**: 确保 `requirements.txt` 和 `package.json` 正确
- **端口配置**: 确保应用监听正确的端口

#### 2. 数据库连接失败
- **检查连接字符串**: 确保 `DATABASE_URL` 正确
- **数据库状态**: 确保数据库服务正在运行
- **网络连接**: 检查服务间网络连接

#### 3. 前端无法访问API
- **CORS问题**: 检查前端配置的API地址
- **代理配置**: 确保Nginx代理配置正确
- **服务状态**: 确保Backend服务正在运行

#### 4. 构建失败
- **Dockerfile**: 检查Dockerfile语法
- **依赖版本**: 确保依赖版本兼容
- **构建上下文**: 确保文件路径正确

### 调试命令

```bash
# 查看服务日志
railway logs --service backend
railway logs --service frontend

# 重启服务
railway restart --service backend
railway restart --service frontend

# 检查环境变量
railway env --service backend
railway env --service frontend

# 进入容器
railway ssh --service backend
railway ssh --service frontend
```

## 📊 监控和维护

### 监控指标

- **CPU使用率**: 在Railway仪表板中查看
- **内存使用**: 监控应用内存消耗
- **请求响应时间**: API性能监控
- **错误率**: 监控应用错误

### 定期维护

1. **更新依赖**
   ```bash
   # 更新Python依赖
   pip install --upgrade -r requirements.txt
   
   # 更新Node.js依赖
   npm update
   ```

2. **备份数据**
   - 定期备份PostgreSQL数据库
   - 使用Railway的备份功能

3. **性能优化**
   - 监控查询性能
   - 优化数据库索引
   - 调整缓存策略

## 🚀 生产环境最佳实践

### 安全性
- 使用HTTPS
- 设置适当的CORS策略
- 定期轮换密钥和密码
- 限制API访问权限

### 性能
- 使用CDN加速静态资源
- 启用数据库连接池
- 实施缓存策略
- 优化查询性能

### 可靠性
- 设置适当的健康检查
- 配置自动重启策略
- 实施监控和告警
- 准备灾难恢复方案

## 📞 支持

如有问题，请查看：
- [Railway文档](https://docs.railway.app)
- [GitHub Issues](https://github.com/your-username/your-repo/issues)
- 项目文档