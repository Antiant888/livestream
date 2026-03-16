# 简化测试方案

如果您无法启动前端界面，可以使用以下简化方案来测试和使用系统。

## 方案1: 仅使用后端API（推荐）

### 启动后端服务
```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
playwright install

# 启动后端服务
python main.py
```

### 使用Swagger UI测试API
1. 打开浏览器访问: `http://localhost:8000/docs`
2. 这会显示API文档界面
3. 可以直接在网页中测试所有API接口

### 生成和查看数据
在Swagger UI中依次执行：

1. **生成模拟数据**
   - 找到 `POST /api/scrape/mock` 接口
   - 点击"Try it out"
   - 点击"Execute"

2. **进行数据分析**
   - 找到 `POST /api/analyze` 接口
   - 点击"Try it out"
   - 点击"Execute"

3. **查看结果**
   - `GET /api/hashtags/frequency` - 查看话题频率
   - `GET /api/trends` - 查看热门话题
   - `GET /api/streams` - 查看直播流
   - `GET /api/stats/realtime` - 查看实时统计

## 方案2: 使用curl命令测试

### 生成模拟数据
```bash
# 生成模拟数据
curl -X POST http://localhost:8000/api/scrape/mock

# 进行分析
curl -X POST http://localhost:8000/api/analyze
```

### 查看数据
```bash
# 查看话题频率分析
curl http://localhost:8000/api/hashtags/frequency

# 查看热门话题
curl http://localhost:8000/api/trends

# 查看直播流
curl http://localhost:8000/api/streams

# 查看实时统计
curl http://localhost:8000/api/stats/realtime
```

## 方案3: 使用Postman测试

### 导入API集合
1. 下载Postman应用
2. 访问 `http://localhost:8000/docs`
3. 点击右上角的"Export"按钮
4. 导出为Postman集合
5. 在Postman中导入并测试

### 手动创建请求
在Postman中创建以下请求：

**POST http://localhost:8000/api/scrape/mock**
- Method: POST
- Body: (空)

**POST http://localhost:8000/api/analyze**
- Method: POST
- Body: (空)

**GET http://localhost:8000/api/hashtags/frequency**
- Method: GET
- Params: time_window=24, limit=100

**GET http://localhost:8000/api/trends**
- Method: GET
- Params: time_window=24, min_frequency=5, min_velocity=0.5

## 方案4: 直接查看数据库

### 使用psql命令行
```bash
# 连接到数据库
psql -U username -d glonghui_analysis

# 查看直播流数据
SELECT * FROM live_streams LIMIT 10;

# 查看话题数据
SELECT * FROM stream_content WHERE hashtags IS NOT NULL LIMIT 10;

# 查看热门话题
SELECT * FROM trending_topics ORDER BY score DESC LIMIT 10;
```

### 使用pgAdmin
1. 打开pgAdmin
2. 连接到PostgreSQL服务器
3. 找到数据库 `glonghui_analysis`
4. 查看各个数据表的内容

## 方案5: 简单的HTML查看器

创建一个简单的HTML文件来查看数据：

```html
<!DOCTYPE html>
<html>
<head>
    <title>格隆汇数据分析 - 简易查看器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>格隆汇数据分析 - 简易查看器</h1>
        
        <div class="card">
            <h3>控制面板</h3>
            <button onclick="generateData()">生成模拟数据</button>
            <button onclick="analyzeData()">分析数据</button>
            <button onclick="refreshAll()">刷新所有数据</button>
        </div>

        <div class="card">
            <h3>实时统计</h3>
            <div id="stats"></div>
        </div>

        <div class="card">
            <h3>热门话题</h3>
            <div id="trends"></div>
        </div>

        <div class="card">
            <h3>话题频率</h3>
            <div id="hashtags"></div>
        </div>

        <div class="card">
            <h3>直播流</h3>
            <div id="streams"></div>
        </div>
    </div>

    <script>
        async function fetchData(url) {
            try {
                const response = await fetch(url);
                return await response.json();
            } catch (error) {
                console.error('Error:', error);
                return null;
            }
        }

        async function generateData() {
            await fetchData('/api/scrape/mock');
            await fetchData('/api/analyze');
            refreshAll();
        }

        async function analyzeData() {
            await fetchData('/api/analyze');
            refreshAll();
        }

        async function refreshAll() {
            // 获取实时统计
            const stats = await fetchData('/api/stats/realtime');
            if (stats) {
                document.getElementById('stats').innerHTML = `
                    <p>最近内容数: ${stats.recent_content_count}</p>
                    <p>最近话题数: ${stats.recent_hashtag_count}</p>
                    <p>活跃趋势: ${stats.active_trends}</p>
                    <p>最后更新: ${stats.timestamp}</p>
                `;
            }

            // 获取热门话题
            const trends = await fetchData('/api/trends');
            if (trends && trends.trends) {
                const trendsHtml = trends.trends.map(trend => `
                    <div style="border:1px solid #ccc; padding:10px; margin:5px;">
                        <h4>${trend.topic_name}</h4>
                        <p>分数: ${trend.score}</p>
                        <p>频率: ${trend.frequency}</p>
                        <p>速度: ${trend.velocity}</p>
                        <p>信心: ${(trend.confidence * 100).toFixed(0)}%</p>
                    </div>
                `).join('');
                document.getElementById('trends').innerHTML = trendsHtml;
            }

            // 获取话题频率
            const hashtags = await fetchData('/api/hashtags/frequency');
            if (hashtags && hashtags.hashtags) {
                const hashtagsHtml = hashtags.hashtags.slice(0, 20).map(hashtag => `
                    <div style="border:1px solid #ccc; padding:10px; margin:5px;">
                        <h4>#${hashtag.hashtag}</h4>
                        <p>频率: ${hashtag.frequency}</p>
                        <p>速度: ${hashtag.velocity}</p>
                        <p>流数: ${hashtag.stream_count}</p>
                    </div>
                `).join('');
                document.getElementById('hashtags').innerHTML = hashtagsHtml;
            }

            // 获取直播流
            const streams = await fetchData('/api/streams');
            if (streams && streams.streams) {
                const streamsHtml = streams.streams.map(stream => `
                    <div style="border:1px solid #ccc; padding:10px; margin:5px;">
                        <h4>${stream.title}</h4>
                        <p>状态: ${stream.status}</p>
                        <p>观众数: ${stream.viewer_count}</p>
                        <p>频道: ${stream.channel_name}</p>
                    </div>
                `).join('');
                document.getElementById('streams').innerHTML = streamsHtml;
            }
        }

        // 页面加载时刷新数据
        window.onload = refreshAll;
    </script>
</body>
</html>
```

将上述HTML保存为 `simple_viewer.html`，然后：

1. 启动后端服务
2. 在浏览器中打开 `simple_viewer.html`
3. 点击按钮生成和查看数据

## 方案6: Python脚本测试

创建一个Python脚本来测试系统：

```python
import requests
import json
import time

def test_system():
    base_url = "http://localhost:8000"
    
    print("=== 格隆汇数据分析系统测试 ===\n")
    
    # 1. 生成模拟数据
    print("1. 生成模拟数据...")
    response = requests.post(f"{base_url}/api/scrape/mock")
    if response.status_code == 200:
        print("✓ 模拟数据生成成功")
    else:
        print("✗ 模拟数据生成失败")
        return
    
    # 2. 进行分析
    print("2. 进行数据分析...")
    response = requests.post(f"{base_url}/api/analyze")
    if response.status_code == 200:
        print("✓ 数据分析成功")
    else:
        print("✗ 数据分析失败")
        return
    
    # 3. 查看实时统计
    print("3. 查看实时统计...")
    response = requests.get(f"{base_url}/api/stats/realtime")
    if response.status_code == 200:
        stats = response.json()
        print(f"   最近内容数: {stats.get('recent_content_count', 0)}")
        print(f"   最近话题数: {stats.get('recent_hashtag_count', 0)}")
        print(f"   活跃趋势: {stats.get('active_trends', 0)}")
    
    # 4. 查看热门话题
    print("4. 查看热门话题...")
    response = requests.get(f"{base_url}/api/trends")
    if response.status_code == 200:
        trends = response.json()
        print(f"   检测到 {len(trends.get('trends', []))} 个热门话题")
        for i, trend in enumerate(trends.get('trends', [])[:5]):
            print(f"   {i+1}. {trend['topic_name']} (分数: {trend['score']})")
    
    # 5. 查看话题频率
    print("5. 查看话题频率...")
    response = requests.get(f"{base_url}/api/hashtags/frequency?limit=10")
    if response.status_code == 200:
        hashtags = response.json()
        print(f"   分析了 {len(hashtags.get('hashtags', []))} 个话题")
        for i, hashtag in enumerate(hashtags.get('hashtags', [])[:5]):
            print(f"   {i+1}. #{hashtag['hashtag']} (频率: {hashtag['frequency']})")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_system()
```

将上述代码保存为 `test_system.py`，然后运行：

```bash
python test_system.py
```

## 总结

即使前端无法启动，您仍然可以通过以下方式使用系统：

1. **Swagger UI**: `http://localhost:8000/docs` - 最推荐
2. **curl命令**: 命令行测试
3. **Postman**: 图形化API测试工具
4. **数据库查看**: 直接查看数据表
5. **简单HTML查看器**: 自定义查看界面
6. **Python脚本**: 自动化测试

建议优先使用 **Swagger UI** (`http://localhost:8000/docs`)，这是最简单和直观的方式。