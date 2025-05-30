# FinTechAI - 智能股票监控平台

一个基于React + Flask的智能股票价格监控和分析平台，集成AI分析功能，支持实时价格提醒和个性化投资建议。

## 📋 项目简介

FinTechAI是一个现代化的股票监控应用，帮助投资者实时跟踪关注股票的价格变动，设置智能提醒阈值，并获得AI驱动的投资分析建议。

## ✨ 主要功能

### 用户认证系统
- 用户注册/登录/登出
- 基于Cookie的会话管理  
- 密码安全验证

### 股票监控
- 添加/删除关注股票
- 实时价格获取和显示
- 自定义价格提醒阈值（上限/下限）
- 价格突破提醒通知

### 个人设置
- Tushare API配置
- 邮箱SMTP设置
- AI API密钥管理
- 个人信息修改

### AI智能分析
- 价格趋势分析
- 投资建议生成
- 风险评估提示

### 提醒日志
- 历史提醒记录查询
- 按时间/股票代码筛选
- 分页浏览支持

## 🛠 技术栈

### 前端 (React)
- **框架**: React 18 + TypeScript
- **UI样式**: Tailwind CSS
- **路由**: React Router DOM
- **状态管理**: React Context API
- **HTTP客户端**: Fetch API
- **构建工具**: Create React App

### 后端 (Flask)
- **框架**: Flask + Python 3.11
- **数据库**: SQLite
- **认证**: Flask Session
- **数据接口**: Tushare API
- **邮件服务**: SMTP

## 📁 项目结构

```
FinTechAI/
├── web/                    # React前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── contexts/      # React Context
│   │   ├── services/      # API服务
│   │   ├── types/         # TypeScript类型定义
│   │   └── App.tsx        # 主应用组件
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
├── Ser/                   # Flask后端服务
│   ├── services/          # 业务逻辑服务
│   ├── data/             # 数据存储
│   ├── app.py            # Flask应用入口
│   ├── config.py         # 配置文件
│   └── requirements.txt  # Python依赖
└── README.md             # 项目说明文档
```

## 🚀 快速开始

### 环境要求
- Node.js >= 16.0.0
- Python >= 3.8
- npm 或 yarn

### 1. 克隆项目
```bash
git clone <repository-url>
cd FinTechAI
```

### 2. 后端服务启动

进入后端目录：
```bash
cd Ser
```

安装Python依赖：
```bash
pip install -r requirements.txt
```

配置环境变量：
```bash
# 复制配置文件
cp env.example .env

# 编辑.env文件，填入相关API密钥
# - TUSHARE_TOKEN: Tushare数据接口令牌
# - SECRET_KEY: Flask会话密钥
# - EMAIL_* : SMTP邮箱配置
```

启动Flask服务：
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 3. 前端应用启动

新开终端，进入前端目录：
```bash
cd web
```

安装依赖：
```bash
npm install
```

启动开发服务器：
```bash
npm start
```

应用将在 `http://localhost:3000` 启动

## 🔑 API接口说明

### 认证接口
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册  
- `POST /auth/logout` - 用户登出
- `GET /auth/check_session` - 会话验证

### 股票管理
- `GET /api/watchlist` - 获取关注列表
- `POST /api/add_stock` - 添加股票
- `DELETE /api/remove_stock` - 删除股票
- `PUT /api/update_stock` - 更新阈值
- `GET /api/stock_search` - 股票搜索
- `GET /api/stock_price/{code}` - 获取股票价格

### 用户设置
- `GET /api/user/settings` - 获取用户设置
- `POST /api/user/settings` - 更新用户设置
- `PUT /api/user/password` - 修改密码

### 提醒系统
- `GET /api/check_alerts_status` - 检查提醒状态
- `GET /api/alert_log` - 获取提醒日志

## 📱 使用说明

1. **用户注册**: 首次使用需要注册账号
2. **基础配置**: 登录后在设置页面配置Tushare Token等信息
3. **添加股票**: 在监控页面添加要关注的股票并设置提醒阈值
4. **查看提醒**: 系统会在价格突破阈值时发送提醒通知
5. **AI分析**: 点击股票卡片查看AI生成的投资分析

## 🔧 开发说明

### 代码规范
- 前端使用TypeScript，严格类型检查
- 组件采用函数式组件 + Hooks
- CSS使用Tailwind原子化类名
- API调用统一通过service层封装

### 构建部署
```bash
# 前端构建
cd web
npm run build

# 后端部署
cd Ser
# 配置生产环境变量
python app.py
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

此项目基于MIT许可证开源。详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

---

**注意**: 使用本应用需要有效的Tushare API Token。请访问 [Tushare官网](https://tushare.pro/) 申请。 