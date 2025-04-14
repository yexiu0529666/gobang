# 五子棋对战平台

一个基于Vue.js和Flask的五子棋对战平台，支持实时对战、历史回放、排行榜等功能。

## 功能特点

- 用户注册和登录
- 实时对战匹配
- 五子棋游戏逻辑
- 历史对局回放
- 个人战绩统计
- 排行榜系统

## 技术栈

### 前端
- Vue.js 3
- Vuex
- Vue Router
- Element Plus
- Socket.io-client

### 后端
- Python 3
- Flask
- Flask-SocketIO
- Flask-SQLAlchemy
- Flask-Login

## 项目结构

```
.
├── gobang/                 # 后端代码
│   ├── app/               # 应用主目录
│   │   ├── __init__.py   # 应用初始化
│   │   ├── models.py     # 数据模型
│   │   ├── auth.py       # 认证相关
│   │   ├── game.py       # 游戏逻辑
│   │   └── replay.py     # 回放功能
│   ├── requirements.txt  # 依赖包
│   └── run.py           # 启动脚本
│
└── gobang-fe/            # 前端代码
    ├── src/             # 源代码
    │   ├── components/  # 组件
    │   ├── views/       # 页面
    │   ├── router/      # 路由
    │   ├── store/       # 状态管理
    │   └── App.vue      # 根组件
    └── package.json     # 依赖配置
```

## 安装和运行

### 后端

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
cd gobang
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

4. 运行服务器：
```bash
python run.py
```

### 前端

1. 安装依赖：
```bash
cd gobang-fe
npm install
```

2. 运行开发服务器：
```bash
npm run serve
```

3. 构建生产版本：
```bash
npm run build
```

## 使用说明

1. 访问 http://localhost:8080 进入平台
2. 注册新账号或登录已有账号
3. 点击"开始对战"进行游戏匹配
4. 在个人中心查看战绩和回放
5. 在首页查看排行榜

## 注意事项

- 确保已安装Node.js和Python 3
- 后端服务器默认运行在5000端口
- 前端开发服务器默认运行在8080端口
- 生产环境部署时注意修改相关配置 