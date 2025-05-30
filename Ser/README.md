# 股票盯盘应用后端

这是一个使用Flask框架开发的股票盯盘应用后端，提供股票价格查询API和股票关注列表管理功能，以及股票价格阈值监控服务。

## 功能

- 获取A股股票实时价格
- 管理用户关注的股票列表
- 监控股票价格是否突破设定阈值
- 通过邮件自动提醒用户价格突破
- 提供RESTful API接口

## 安装与配置

1. 安装依赖项：

```bash
pip install -r requirements.txt
```

2. 配置环境变量：

创建`.env`文件，添加以下配置：

```
# Tushare API Token
TUSHARE_TOKEN=your_tushare_token_here

# 邮件配置
SMTP_SERVER=smtp.163.com
SMTP_PORT=25
SMTP_USE_SSL=False
SMTP_USERNAME=your_email@163.com
SMTP_PASSWORD=your_email_password_or_authorization_code
EMAIL_SENDER=your_email@163.com
ENABLE_EMAIL_ALERTS=True

# Flask配置
FLASK_DEBUG=1
FLASK_PORT=5000
```

> 注意：对于大多数邮箱服务，`SMTP_PASSWORD`需要使用授权码而非登录密码。

## 运行

```bash
python app.py
```

服务将在本地5000端口启动，并自动开始监控任务。

## API接口

### 获取股票价格

- **URL**: `/api/stock_price/<stock_code>`
- **方法**: GET
- **URL参数**: 
  - `stock_code`: A股股票代码，例如 `600036.SH`
- **成功响应**:
  - 状态码: 200
  - 内容示例: `{"code": "600036.SH", "price": 39.85}`
- **错误响应**:
  - 状态码: 404
  - 内容示例: `{"error": "无法获取股票价格"}`

### 添加关注股票

- **URL**: `/api/add_stock`
- **方法**: POST
- **请求体**:
  ```json
  {
    "stock_code": "600036.SH",
    "stock_name": "招商银行",
    "upper_threshold": 45.50,
    "lower_threshold": 35.80,
    "user_email": "user@example.com"
  }
  ```
- **成功响应**:
  - 状态码: 201
  - 内容示例: `{"message": "股票添加成功"}`
- **错误响应**:
  - 状态码: 400
  - 内容示例: `{"error": "输入数据格式不正确"}`

### 获取关注列表

- **URL**: `/api/watchlist`
- **方法**: GET
- **成功响应**:
  - 状态码: 200
  - 内容示例: 
    ```json
    [
      {
        "stock_code": "600036.SH",
        "stock_name": "招商银行",
        "upper_threshold": 45.50,
        "lower_threshold": 35.80,
        "user_email": "user@example.com",
        "added_at": "2023-05-01 12:34:56"
      }
    ]
    ```

### 立即执行监控检查

- **URL**: `/api/check_now`
- **方法**: GET
- **成功响应**:
  - 状态码: 200
  - 内容示例: `{"message": "监控检查已触发"}`

## 监控系统

系统会自动定时（每分钟）检查所有关注股票的价格是否突破设定的上下限阈值。当价格突破阈值时，系统会记录警报信息，并通过以下方式通知用户：

1. 日志记录：所有警报都会记录在日志文件中
2. 邮件通知：当价格突破阈值时，系统会自动向用户发送邮件提醒

### 邮件提醒配置

要启用邮件提醒功能，请在`.env`文件中设置以下参数：

- `SMTP_SERVER`: SMTP服务器地址（如 smtp.163.com）
- `SMTP_PORT`: SMTP服务器端口（通常为25或465）
- `SMTP_USE_SSL`: 是否使用SSL连接（True/False）
- `SMTP_USERNAME`: 邮箱账号
- `SMTP_PASSWORD`: 邮箱密码或授权码
- `EMAIL_SENDER`: 发件人邮箱（通常与SMTP_USERNAME相同）
- `ENABLE_EMAIL_ALERTS`: 是否启用邮件提醒（True/False）

您可以使用以下命令测试邮件发送功能：

```bash
python test_email.py
```

## 开发说明

- `app.py`: Flask应用主入口，集成了定时监控功能
- `services/`: 服务层，包含业务逻辑
  - `stock_service.py`: 股票数据服务，处理股票价格获取逻辑
  - `watchlist_service.py`: 关注列表服务，处理股票关注列表管理
  - `monitor_service.py`: 监控服务，检查股票价格是否突破阈值
  - `email_service.py`: 邮件服务，处理邮件发送功能
- `data/`: 数据存储目录
  - `watchlist.json`: 存储用户关注的股票列表
- `scheduler_apscheduler.py`: 使用APScheduler实现的独立监控服务
- `scheduler_simple.py`: 使用简单循环实现的独立监控服务
- `test_monitor.py`: 测试监控功能的脚本
- `test_email.py`: 测试邮件发送功能的脚本

## 定时监控实现方案

本项目提供了三种定时监控的实现方案：

1. **集成在Flask应用中** (默认使用)
   - 优点：与Web服务集成，无需额外进程
   - 缺点：依赖Flask应用运行，重启Flask会重置调度器

2. **APScheduler独立脚本**
   - 运行方式：`python scheduler_apscheduler.py`
   - 优点：功能丰富，支持复杂调度，持久化作业
   - 缺点：依赖额外库

3. **简单循环独立脚本**
   - 运行方式：`python scheduler_simple.py`
   - 优点：简单直观，无额外依赖
   - 缺点：不支持复杂调度，无法持久化

## 测试

可以使用提供的测试脚本来测试API和其他功能:

```bash
# 测试API
python test_api.py

# 测试监控功能
python test_monitor.py

# 测试邮件功能
python test_email.py
``` 