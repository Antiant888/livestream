# 快速启动指南

## 系统要求

- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 12+**
- **Windows 10/11** (本项目在Windows环境下开发)

## 快速安装

### 方法1: 使用一键启动脚本（推荐）

1. 双击运行 `setup_and_run.bat` 文件
2. 按照提示操作
3. 等待系统自动启动

### 方法2: 手动安装

#### 1. 后端设置
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install

# 启动后端服务
python main.py
```

#### 2. 前端设置（新终端窗口）
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端服务
npm run dev
```

## 数据库设置

### 创建数据库
```sql
-- 在PostgreSQL中执行
CREATE DATABASE glonghui_analysis;
```

### 环境变量设置
在 `backend` 目录下创建 `.env` 文件：
```
DATABASE_URL=postgresql://username:password@localhost:5432/glonghui_analysis
```

## 启动服务

### 后端API服务
- 地址: `http://localhost:8000`
- 自动初始化数据库

### 前端界面
- 地址: `http://localhost:3000`
- 需要等待后端启动完成

## 生成测试数据

### 使用API命令
```bash
# 生成模拟数据
curl -X POST http://localhost:8000/api/scrape/mock

# 进行数据分析
curl -X POST http://localhost:8000/api/analyze
```

### 在仪表板中操作
1. 打开 `http://localhost:3000`
2. 点击"刷新数据"按钮
3. 系统会自动生成模拟数据并进行分析

## 访问功能

### 仪表板功能
- **实时概览**: 查看关键指标
- **直播流**: 监控模拟直播状态
- **话题分析**: 查看话题频率统计
- **热门话题**: 查看趋势检测结果

### API接口测试
- 访问 `http://localhost:8000/docs` 查看API文档
- 使用Swagger UI测试各种接口

## 常见问题

### 1. Python环境问题
```
错误: 未找到Python
```
**解决**: 安装Python 3.9+ 并添加到系统PATH

### 2. Node.js环境问题
```
错误: 未找到Node.js
```
**解决**: 安装Node.js 16+ 并添加到系统PATH

### 3. 数据库连接问题
```
无法连接到PostgreSQL
```
**解决**: 
- 确保PostgreSQL服务正在运行
- 检查连接字符串是否正确
- 确认数据库已创建

### 4. 端口占用问题
```
Address already in use
```
**解决**: 
- 检查端口8000和3000是否被占用
- 关闭占用端口的程序
- 或修改配置文件中的端口号

### 5. 依赖安装问题
```
pip install 失败
```
**解决**: 
- 升级pip: `python -m pip install --upgrade pip`
- 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

## 项目结构说明

```
glonghui-analysis/
├── backend/           # 后端服务
│   ├── main.py       # API入口
│   ├── models/       # 数据模型
│   ├── scrapers/     # 数据抓取器
│   └── analysis/     # 分析引擎
├── frontend/          # 前端应用
│   ├── src/          # React组件
│   ├── package.json  # 前端依赖
│   └── index.html    # 入口文件
├── docs/             # 文档
└── setup_and_run.bat # 一键启动脚本
```

## 开发说明

### 修改模拟数据
编辑 `backend/scrapers/mock_scraper.py` 文件：
- 修改话题列表
- 调整用户行为
- 自定义情感分析规则

### 添加新功能
- 后端: 在 `backend/` 目录下添加新的API端点
- 前端: 在 `frontend/src/components/` 下添加新组件
- 数据库: 在 `backend/models/` 下添加新模型

## 技术支持

如有问题，请查看：
- `README.md` - 详细文档
- `docs/` - 技术文档
- 项目注释 - 代码说明

## 许可证

MIT License