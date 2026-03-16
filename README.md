# 格隆汇 Live Streaming Analysis System

一个用于分析格隆汇直播流数据的完整系统，包括数据抓取、存储、分析和可视化功能。

## 项目概述

本项目旨在通过分析格隆汇（https://www.gelonghui.com/live?channelId=all）的直播流数据，提取有价值的信息并进行实时分析，包括：

- **实时数据抓取**：从格隆汇网站抓取直播流元数据和聊天内容
- **话题频率分析**：分析话题标签的出现频率和传播速度
- **趋势检测**：识别热门话题和趋势
- **情感分析**：分析用户情感倾向
- **数据可视化**：通过交互式仪表板展示分析结果

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 Dashboard │ ←→ │   FastAPI 后端   │ ←→ │   PostgreSQL    │
│   (React + MUI)  │    │   (Python)      │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ↓
                       ┌─────────────────┐
                       │   数据抓取器     │
                       │   (Playwright)  │
                       └─────────────────┘
                                │
                                ↓
                       ┌─────────────────┐
                       │   分析引擎      │
                       │   (Hashtag     │
                       │    Analyzer)   │
                       └─────────────────┘
```

## 技术栈

### 后端 (Python)
- **FastAPI**: Web API 框架
- **SQLAlchemy**: ORM 数据库操作
- **Playwright**: 浏览器自动化抓取
- **PostgreSQL**: 主数据库
- **Celery**: 任务队列（可选）
- **Loguru**: 日志管理

### 前端 (JavaScript/TypeScript)
- **React**: 前端框架
- **TypeScript**: 类型安全
- **Material-UI**: UI 组件库
- **Chart.js**: 数据可视化
- **Vite**: 构建工具

### 数据库
- **PostgreSQL**: 主数据库
- **Redis**: 缓存（可选）

## 项目结构

```
glonghui-analysis/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py           # 基础模型
│   │   ├── live_streams.py   # 直播流模型
│   │   ├── stream_content.py # 内容模型
│   │   └── hashtags.py       # 话题模型
│   ├── database/             # 数据库配置
│   │   ├── __init__.py
│   │   └── config.py         # 数据库连接
│   ├── scrapers/             # 抓取器
│   │   ├── __init__.py
│   │   ├── base_scraper.py   # 基础抓取器
│   │   └── glonghui_scraper.py # 格隆汇专用抓取器
│   └── analysis/             # 分析引擎
│       ├── __init__.py
│       └── hashtag_analyzer.py # 话题分析器
├── frontend/                   # 前端应用
│   ├── package.json           # 前端依赖
│   ├── vite.config.ts         # Vite 配置
│   ├── tsconfig.json          # TypeScript 配置
│   ├── index.html             # HTML 入口
│   └── src/                   # 源代码
│       ├── main.tsx          # 应用入口
│       ├── App.tsx           # 主应用组件
│       └── components/       # React 组件
│           ├── Dashboard.tsx
│           ├── LiveStreams.tsx
│           ├── HashtagAnalysis.tsx
│           ├── TrendingTopics.tsx
│           └── Navigation.tsx
├── docs/                      # 文档
│   └── website_analysis_report.md # 网站分析报告
└── README.md                  # 项目说明
```

## 安装和配置

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis (可选)

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install

# 设置环境变量
echo "DATABASE_URL=postgresql://username:password@localhost:5432/glonghui_analysis" > .env
```

### 3. 数据库设置

```bash
# 创建数据库
createdb glonghui_analysis

# 运行数据库初始化（启动应用时自动执行）
python -c "from database.config import init_db; init_db()"
```

### 4. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 启动应用

```bash
# 启动后端 API
cd backend
python main.py

# 在另一个终端启动前端
cd frontend
npm run dev
```

## API 接口

### 数据抓取接口

- `POST /api/scrape` - 手动触发真实数据抓取（需要网络访问）
- `POST /api/scrape/mock` - 手动触发模拟数据生成（推荐用于测试）
- `POST /api/analyze` - 手动触发数据分析

### 数据查询接口

- `GET /api/streams` - 获取所有直播流
- `GET /api/streams/{stream_id}/content` - 获取特定直播流内容
- `GET /api/hashtags/frequency` - 获取话题频率分析
- `GET /api/trends` - 获取热门话题
- `GET /api/trends/sentiment` - 获取情感分析
- `GET /api/stats/realtime` - 获取实时统计

### 模拟数据系统

由于网络访问限制，系统提供了完整的模拟数据生成器：

- **MockScraper**: 生成逼真的模拟直播流数据
- **话题数据**: 包含中英文财经、科技、投资等热门话题
- **情感分析**: 模拟用户情感倾向和评论内容
- **实时更新**: 支持动态数据生成和更新

**使用方法**：
```bash
# 生成模拟数据
curl -X POST http://localhost:8000/api/scrape/mock

# 然后进行分析
curl -X POST http://localhost:8000/api/analyze
```

## 功能特性

### 1. 实时数据抓取
- 自动检测直播流状态变化
- 抓取聊天消息和评论
- 提取话题标签和用户提及
- 基础情感分析

### 2. 话题分析
- 话题频率统计
- 话题传播速度计算
- 跨直播流话题追踪
- 话题生命周期分析

### 3. 趋势检测
- 基于频率和速度的趋势评分
- 信心度计算
- 趋势预测
- 历史趋势对比

### 4. 情感分析
- 正负面情感识别
- 情感波动性分析
- 情感趋势追踪
- 情感分布统计

### 5. 数据可视化
- 实时仪表板
- 话题频率图表
- 趋势热力图
- 情感分析图表
- 响应式设计

## 使用说明

### 1. 访问仪表板
打开浏览器访问 `http://localhost:3000` 查看数据仪表板。

### 2. 监控直播流
在"直播流"页面查看当前所有直播流的状态和观众数。

### 3. 分析话题趋势
在"话题分析"和"热门话题"页面查看话题频率和趋势分析。

### 4. 手动触发分析
可以通过 API 接口或仪表板上的按钮手动触发数据抓取和分析。

## 配置选项

### 抓取器配置
```python
# 在 glonghui_scraper.py 中配置
delay_range = (2, 5)  # 请求间隔（秒）
```

### 分析器配置
```python
# 在 hashtag_analyzer.py 中配置
time_window = 24      # 分析时间窗口（小时）
min_frequency = 5     # 最小频率阈值
min_velocity = 0.5    # 最小速度阈值
```

### 数据库配置
```python
# 在 database/config.py 中配置
DATABASE_URL = "postgresql://user:pass@host:port/db"
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t glonghui-analysis .

# 运行容器
docker run -p 8000:8000 glonghui-analysis
```

### 生产环境部署

1. 使用 Gunicorn 或 uWSGI 运行后端
2. 使用 Nginx 作为反向代理
3. 配置 PostgreSQL 生产环境
4. 设置定时任务进行定期抓取

## 监控和维护

### 日志监控
- 使用 Loguru 记录详细日志
- 监控抓取成功率
- 跟踪分析性能

### 性能优化
- 数据库索引优化
- 缓存策略实施
- 异步处理优化

### 数据备份
- 定期备份 PostgreSQL 数据
- 实施数据恢复策略

## 法律和伦理考虑

### 合规性
- 遵守目标网站的使用条款
- 尊重 robots.txt 规则
- 实施合理的请求频率限制

### 数据隐私
- 不存储敏感个人信息
- 匿名化处理用户数据
- 遵守数据保护法规

## 故障排除

### 常见问题

1. **抓取失败**
   - 检查网络连接
   - 验证目标网站是否可访问
   - 调整请求延迟

2. **数据库连接错误**
   - 检查 PostgreSQL 服务状态
   - 验证连接字符串
   - 确认数据库权限

3. **前端无法访问后端**
   - 检查 CORS 配置
   - 验证代理设置
   - 确认端口开放

### 调试工具

- 使用浏览器开发者工具监控网络请求
- 查看后端日志文件
- 使用数据库客户端检查数据

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

## 更新日志

### v1.0.0 (2026-03-16)
- 初始版本发布
- 完整的数据抓取和分析功能
- 响应式 Web 仪表板
- PostgreSQL 数据库集成