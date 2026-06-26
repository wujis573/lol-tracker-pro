# LOL 战绩查询

英雄联盟国服战绩查询 Web 应用，支持召唤师搜索、排位信息、对局记录、数据统计和排行榜。

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Vue](https://img.shields.io/badge/Vue-3.4-blue)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-cyan)

## 功能

- 召唤师搜索与个人档案
- 排位段位与胜率
- 最近对局记录（KDA / 装备 / 符文）
- 数据统计（近 N 场平均 KDA、胜率、常用英雄）
- 最强王者 / 傲世宗师排行榜
- 异常处理友好提示

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + aiohttp |
| 前端 | Vue 3 + TailwindCSS |
| 数据 | Riot API（国服代理）+ OP.GG API |
| 缓存 | Redis（可选，无 Redis 自动降级为内存缓存） |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- pnpm（推荐）或 npm

### 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入配置

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 启动
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `RIOT_GATEWAY_URL` | 国服 Riot API 地址 | `https://api.riot-gateway.cn` |
| `RIOT_API_KEY` | Riot API Key（可选） | 空 |
| `OPGG_API_URL` | OP.GG API 地址 | `https://api.op.gg` |
| `OPGG_API_KEY` | OP.GG API Key（可选） | 空 |
| `CACHE_TTL` | 缓存有效期（秒） | `300` |
| `RATE_LIMIT_PER_SECOND` | 每秒请求限制 | `20` |
| `RATE_LIMIT_PER_MINUTE` | 每分钟请求限制 | `100` |

## 部署

### 后端部署（Render）

1. 创建 Render 账号并连接 GitHub
2. 新建 Web Service，选择本项目
3. 设置环境变量
4. 构建命令：`pip install -r backend/requirements.txt`
5. 启动命令：`cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 前端部署（Vercel / Netlify）

1. 构建命令：`cd frontend && npm install && npm run build`
2. 输出目录：`frontend/dist`
3. 环境变量：`VITE_API_BASE=https://your-backend-url.com/api`

## 目录结构

```
lol-tracker-pro/
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心逻辑（客户端/缓存/模型/异常）
│   │   ├── config.py      # 配置管理
│   │   └── main.py        # FastAPI 入口
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── api/           # API 调用
│   │   └── assets/        # 静态资源
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

## API 文档

后端启动后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/summoner/search?name=xxx` | 搜索召唤师 |
| GET | `/api/summoner/{puuid}/profile` | 召唤师档案 |
| GET | `/api/summoner/{puuid}/matches` | 对局记录 |
| GET | `/api/summoner/{puuid}/stats` | 统计数据 |
| GET | `/api/leaderboard/challenger` | 最强王者排行 |
| GET | `/api/leaderboard/grandmaster` | 傲世宗师排行 |

## 注意事项

- 本工具仅供学习交流使用
- 请遵守 Riot Games 服务条款
- 国服 API 通过第三方代理访问，稳定性取决于代理服务
- 建议部署时使用 CDN 加速静态资源

## License

MIT
