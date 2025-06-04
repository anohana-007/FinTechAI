# FinTechAI - 智能股票监控平台

一个基于React + Flask的智能股票价格监控和分析平台，集成AI分析功能，支持实时价格提醒和个性化投资建议。

## 📋 项目简介

FinTechAI是一个现代化的股票监控应用，帮助投资者实时跟踪关注股票的价格变动，设置智能提醒阈值，并获得AI驱动的投资分析建议。采用响应式设计，支持桌面和移动端访问。

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
- 股票搜索和筛选功能

### 响应式界面设计
- **🎨 全新界面优化**: 完全响应式设计，支持桌面和移动端
- **📱 移动端适配**: 专为移动设备优化的导航和布局
- **⚡ 智能布局**: AI洞察分析面板占据最大空间，优化信息展示
- **🔍 集成搜索**: 股票搜索功能直接集成在监控面板中
- **💼 紧凑设计**: 优化空间利用，重要信息一目了然

### AI智能分析
- **多模型支持**: 支持OpenAI、Gemini、DeepSeek等多种AI模型
- **智能评分**: AI综合评分和投资建议
- **深度分析**: 技术分析、基本面分析、市场情绪分析
- **实时洞察**: 价格突破时自动AI分析
- **置信度评估**: 分析结果的可信度指标

### 个人设置
- Tushare API配置
- 邮箱SMTP设置
- AI API密钥管理（OpenAI、Gemini、DeepSeek等）
- 个人信息修改
- AI模型偏好设置

### 提醒日志
- 历史提醒记录查询
- 按时间/股票代码筛选
- 分页浏览支持
- AI分析结果历史记录

## 🛠 技术栈

### 前端 (React)
- **框架**: React 18 + TypeScript
- **UI样式**: Tailwind CSS（完全响应式设计）
- **路由**: React Router DOM
- **状态管理**: React Context API
- **HTTP客户端**: Fetch API
- **构建工具**: Create React App
- **响应式支持**: 移动端优先设计原则

### 后端 (Flask)
- **框架**: Flask + Python 3.11
- **数据库**: SQLite
- **认证**: Flask Session
- **数据接口**: Tushare API
- **邮件服务**: SMTP
- **AI集成**: 多平台AI API支持

## 📁 项目结构

```
FinTechAI/
├── web/                    # React前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   │   ├── Dashboard.tsx      # 主仪表板（响应式）
│   │   │   ├── AnalysisPanel.tsx  # AI分析面板
│   │   │   ├── StockCard.tsx      # 股票卡片组件
│   │   │   ├── Sidebar.tsx        # 侧边栏导航
│   │   │   ├── MobileNav.tsx      # 移动端导航
│   │   │   └── ...               # 其他组件
│   │   ├── pages/         # 页面组件
│   │   ├── contexts/      # React Context
│   │   ├── services/      # API服务
│   │   ├── types/         # TypeScript类型定义
│   │   └── App.tsx        # 主应用组件
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
├── Ser/                   # Flask后端服务
│   ├── services/          # 业务逻辑服务
│   ├── data/             # 数据存储（SQLite数据库）
│   ├── logs/             # 应用日志
│   ├── app.py            # Flask应用入口
│   └── requirements.txt  # Python依赖
├── logs/                 # 系统日志
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

启动Flask服务：
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动
**注意**: 首次启动时会自动创建数据库，所有配置通过用户设置界面管理，无需环境变量配置。

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

### AI分析接口
- `POST /api/analyze_stock` - 手动触发AI分析
- `GET /api/user/settings/detail` - 获取用户AI配置详情

### 用户设置
- `GET /api/user/settings` - 获取用户设置
- `POST /api/user/settings` - 更新用户设置
- `PUT /api/user/password` - 修改密码

### 提醒系统
- `GET /api/check_alerts_status` - 检查提醒状态
- `GET /api/alert_log` - 获取提醒日志

## 📱 使用说明

### 桌面端
1. **用户注册**: 首次使用需要注册账号
2. **基础配置**: 登录后在设置页面配置Tushare Token和AI API密钥
3. **添加股票**: 在监控页面使用搜索功能添加要关注的股票并设置提醒阈值
4. **AI分析**: 选择AI模型后点击"获取AI分析"查看智能投资建议
5. **查看提醒**: 系统会在价格突破阈值时发送提醒通知并自动进行AI分析

### 移动端
- **响应式导航**: 自动隐藏侧边栏，使用顶部导航栏
- **触摸优化**: 按钮和交互元素针对触摸操作优化
- **紧凑布局**: 信息密度优化，重要内容优先显示
- **全屏体验**: 充分利用移动设备屏幕空间

## 🎨 界面特性

### 响应式设计
- **断点适配**: 支持大屏(lg)、中屏(md)、小屏(sm)等多种屏幕尺寸
- **弹性布局**: 使用Flexbox和Grid实现自适应布局
- **组件复用**: 桌面和移动端共享核心组件逻辑

### 视觉优化
- **渐变背景**: 现代化的渐变色彩搭配
- **阴影层次**: 合理的阴影和深度设计
- **颜色语义**: 用颜色传达信息状态（成功、警告、错误等）
- **字体层次**: 清晰的字体大小和权重层次

### 交互体验
- **加载状态**: 明确的加载和处理状态反馈
- **错误处理**: 友好的错误信息提示
- **操作反馈**: 即时的操作结果反馈
- **快捷操作**: 便捷的快捷键和手势支持

## 🔧 开发说明

### 代码规范
- 前端使用TypeScript，严格类型检查
- 组件采用函数式组件 + Hooks
- CSS使用Tailwind原子化类名，响应式优先
- API调用统一通过service层封装
- 组件复用和模块化设计原则

### 响应式开发
- 移动端优先设计原则
- 使用Tailwind响应式工具类
- 组件级别的响应式处理
- 性能优化和懒加载

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

## 🚀 最新更新

### v2.1.0 - 数据源扩展与系统优化
- ✅ 修复股票代码与名称不匹配问题
- ✅ AI分析提示词优化，提高分析准确性
- ✅ 系统性能优化，减少内存占用
- ✅ 添加BaoStock数据源支持（计划中）
- ✅ 数据库和日志清理功能完善
- ✅ 修复多个AI模型兼容性问题

## 📊 数据源说明

### 现有数据源
- **Tushare API**: 主要用于股票基本信息查询和实时价格获取
- **AkShare**: 用于获取基本面数据

### 计划扩展
- **BaoStock**: 将添加支持以获取更全面的技术面和基本面数据
  - 提供完整K线数据（日K、周K、月K）
  - 支持多种技术指标（MA、MACD、KDJ、RSI等）
  - 季度、年度财务报表数据
  - 多种财务指标（ROE、ROA、毛利率、净利率等）
  - 无需Token认证，免费使用

### 数据整合策略
计划采用混合数据源策略：
- 使用BaoStock获取完整历史数据和基本面
- 保留现有数据源用于实时价格
- 设计数据缓存机制减少API调用频率

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发规范
- 遵循响应式设计原则
- 保持代码的类型安全
- 编写简洁的组件和清晰的API
- 测试不同设备和屏幕尺寸

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

---

**注意**: 
- 使用本应用需要有效的Tushare API Token。请访问 [Tushare官网](https://tushare.pro/) 申请。
- AI分析功能需要配置相应的AI服务API密钥（OpenAI、Gemini等）。
- 建议在现代浏览器中使用以获得最佳体验。 