import os
import threading
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from functools import wraps
from services.stock_service import get_stock_price, search_stocks
from services.watchlist_service import get_watchlist, add_stock, remove_stock, update_stock_thresholds
from services.monitor_service import check_thresholds, format_alert_message, check_and_get_alerts
from services.alert_manager import reset_alert
from services.database_service import get_alert_logs, get_alert_logs_count, init_database
from services.auth_service import (
    init_user_database, register_user, authenticate_user, 
    get_user_by_id, get_user_config, get_user_config_summary, 
    update_user_config, change_password
)
import config
from datetime import datetime

# 加载环境变量
load_dotenv()
print(f"环境变量TUSHARE_TOKEN: {'已设置' if os.getenv('TUSHARE_TOKEN') else '未设置'}")

# 初始化数据库
try:
    init_database()
    init_user_database()
    print("数据库初始化成功")
except Exception as e:
    print(f"数据库初始化失败: {e}")

app = Flask(__name__)

# 配置Flask会话
app.secret_key = config.SECRET_KEY

# 配置CORS，允许前端跨域请求
CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:3000",  # 允许的前端源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的HTTP方法
        "allow_headers": ["Content-Type", "Authorization"],  # 允许的请求头
        "supports_credentials": True  # 允许携带凭证(cookies)
    },
    r"/auth/*": {
        "origins": "http://localhost:3000",  # 允许的前端源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的HTTP方法
        "allow_headers": ["Content-Type", "Authorization"],  # 允许的请求头
        "supports_credentials": True  # 允许携带凭证(cookies)
    }
})

# 认证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "需要登录", "code": "UNAUTHORIZED"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return None
    return get_user_by_id(session['user_id'])

def get_current_user_config():
    """获取当前登录用户的配置"""
    if 'user_id' not in session:
        return None
    return get_user_config(session['user_id'])

# 创建调度器
scheduler = BackgroundScheduler()

# ========== 认证API ==========

@app.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # 基本验证
        if not username or not email or not password:
            return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "用户名至少需要3个字符"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "密码至少需要6个字符"}), 400
        
        # 简单的邮箱格式验证
        if '@' not in email or '.' not in email:
            return jsonify({"error": "无效的邮箱格式"}), 400
        
        # 注册用户
        success, message = register_user(username, email, password)
        
        if success:
            return jsonify({"message": message}), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        app.logger.error(f"用户注册出错: {e}")
        return jsonify({"error": "注册失败，请稍后重试"}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        # 验证用户
        user_info = authenticate_user(username, password)
        
        if user_info:
            # 设置会话
            session['user_id'] = user_info['id']
            session['username'] = user_info['username']
            session.permanent = True  # 使会话持久化
            
            return jsonify({
                "message": "登录成功",
                "user": {
                    "id": user_info['id'],
                    "username": user_info['username'],
                    "email": user_info['email']
                }
            }), 200
        else:
            return jsonify({"error": "用户名或密码错误"}), 401
            
    except Exception as e:
        app.logger.error(f"用户登录出错: {e}")
        return jsonify({"error": "登录失败，请稍后重试"}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({"message": "登出成功"}), 200

@app.route('/auth/check_session', methods=['GET'])
def check_session():
    """检查会话状态"""
    if 'user_id' in session:
        user_info = get_current_user()
        if user_info:
            return jsonify({
                "authenticated": True,
                "user": user_info
            }), 200
    
    return jsonify({"authenticated": False}), 200

@app.route('/auth/user', methods=['GET'])
@login_required
def get_user():
    """获取当前用户信息"""
    user_info = get_current_user()
    if user_info:
        return jsonify({"user": user_info}), 200
    else:
        return jsonify({"error": "用户不存在"}), 404

# ========== 用户设置API ==========

@app.route('/api/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    """获取用户设置"""
    try:
        config_summary = get_user_config_summary(session['user_id'])
        if config_summary:
            return jsonify({
                "success": True,
                "settings": config_summary
            }), 200
        else:
            return jsonify({"error": "获取用户设置失败"}), 500
            
    except Exception as e:
        app.logger.error(f"获取用户设置出错: {e}")
        return jsonify({"error": "获取用户设置失败"}), 500

@app.route('/api/user/settings', methods=['POST'])
@login_required
def update_user_settings():
    """更新用户设置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 准备配置数据
        config_data = {}
        
        # 处理各种配置字段
        if 'tushare_token' in data:
            config_data['tushare_token'] = data['tushare_token'].strip() if data['tushare_token'] else None
        
        if 'email_sender_address' in data:
            config_data['email_sender_address'] = data['email_sender_address'].strip() if data['email_sender_address'] else None
        
        if 'email_smtp_server' in data:
            config_data['email_smtp_server'] = data['email_smtp_server'].strip() if data['email_smtp_server'] else None
        
        if 'email_smtp_port' in data:
            try:
                config_data['email_smtp_port'] = int(data['email_smtp_port']) if data['email_smtp_port'] else 587
            except ValueError:
                return jsonify({"error": "无效的SMTP端口号"}), 400
        
        if 'email_smtp_user' in data:
            config_data['email_smtp_user'] = data['email_smtp_user'].strip() if data['email_smtp_user'] else None
        
        if 'email_smtp_password' in data:
            config_data['email_smtp_password'] = data['email_smtp_password'] if data['email_smtp_password'] else None
        
        if 'ai_api_keys' in data and isinstance(data['ai_api_keys'], dict):
            # 过滤空值
            ai_keys = {k: v for k, v in data['ai_api_keys'].items() if v and v.strip()}
            config_data['ai_api_keys'] = ai_keys if ai_keys else {}
        
        # 更新配置
        success, message = update_user_config(session['user_id'], config_data)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        app.logger.error(f"更新用户设置出错: {e}")
        return jsonify({"error": "更新用户设置失败"}), 500

@app.route('/api/user/password', methods=['PUT'])
@login_required
def change_user_password():
    """修改用户密码"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({"error": "旧密码和新密码不能为空"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "新密码至少需要6个字符"}), 400
        
        # 修改密码
        success, message = change_password(session['user_id'], old_password, new_password)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        app.logger.error(f"修改密码出错: {e}")
        return jsonify({"error": "修改密码失败"}), 500

# ========== 股票API ==========

@app.route('/api/stock_price/<stock_code>')
def stock_price(stock_code):
    """获取指定股票代码的当前价格"""
    # 如果用户已登录，使用用户的配置，否则使用全局配置
    user_config = get_current_user_config()
    price = get_stock_price(stock_code, user_config)
    if price is None:
        return jsonify({"error": "无法获取股票价格"}), 404
    return jsonify({
        "code": stock_code,
        "price": price
    })

@app.route('/api/stock_search')
def stock_search():
    """搜索股票代码和名称"""
    query = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({"error": "搜索关键词不能为空"}), 400
    
    if limit > 50:  # 限制最大返回数量
        limit = 50
    
    try:
        # 如果用户已登录，使用用户的配置，否则使用全局配置
        user_config = get_current_user_config()
        results = search_stocks(query, limit, user_config)
        return jsonify({
            "query": query,
            "count": len(results),
            "results": [{"code": r["code"], "name": r["name"]} for r in results]
        })
    except Exception as e:
        app.logger.error(f"股票搜索出错: {e}")
        return jsonify({"error": "股票搜索失败"}), 500

@app.route('/api/watchlist', methods=['GET'])
def watchlist():
    """获取用户关注的股票列表"""
    stocks = get_watchlist()
    return jsonify(stocks)

@app.route('/api/add_stock', methods=['POST'])
def add_stock_to_watchlist():
    """添加股票到关注列表"""
    data = request.json
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    # 添加股票到关注列表
    success, message = add_stock(data)
    
    if success:
        return jsonify({"message": message}), 201
    else:
        return jsonify({"error": message}), 400

@app.route('/api/remove_stock', methods=['DELETE'])
def remove_stock_from_watchlist():
    """从关注列表中删除股票"""
    data = request.json
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    stock_code = data.get('stock_code')
    user_email = data.get('user_email')
    
    if not stock_code or not user_email:
        return jsonify({"error": "缺少必要参数：stock_code 和 user_email"}), 400
    
    # 从关注列表中删除股票
    success, message = remove_stock(stock_code, user_email)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@app.route('/api/update_stock', methods=['PUT'])
def update_stock_thresholds_api():
    """更新股票的阈值设置"""
    data = request.json
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    stock_code = data.get('stock_code')
    user_email = data.get('user_email')
    upper_threshold = data.get('upper_threshold')
    lower_threshold = data.get('lower_threshold')
    
    if not all([stock_code, user_email, upper_threshold is not None, lower_threshold is not None]):
        return jsonify({"error": "缺少必要参数：stock_code, user_email, upper_threshold, lower_threshold"}), 400
    
    # 更新股票阈值
    success, message = update_stock_thresholds(stock_code, user_email, upper_threshold, lower_threshold)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@app.route('/api/check_now', methods=['GET'])
def check_now():
    """立即执行一次监控检查"""
    # 在新线程中执行检查，避免阻塞API响应
    threading.Thread(target=monitor_job).start()
    return jsonify({"message": "监控检查已触发"}), 200

@app.route('/api/check_alerts_status', methods=['GET'])
def check_alerts_status():
    """
    检查警报状态，用于前端轮询
    
    如果发现突破阈值的股票，返回警报信息
    """
    # 获取警报列表
    alerts = check_and_get_alerts()
    
    # 格式化响应数据
    formatted_alerts = []
    for alert in alerts:
        # 确保字段名称一致
        current_price = alert.get('current_price', alert.get('price'))
        
        formatted_alert = {
            'stock_code': alert['stock_code'],
            'stock_name': alert.get('stock_name', '未知股票'),
            'current_price': current_price,
            'threshold': alert.get('threshold'),
            'direction': alert['direction'],
            'timestamp': alert.get('timestamp'),
            'message': format_alert_message(alert),
            'ai_analysis': alert.get('ai_analysis', '')
        }
        formatted_alerts.append(formatted_alert)
    
    return jsonify({
        "has_alerts": len(formatted_alerts) > 0,
        "alerts": formatted_alerts
    })

@app.route('/api/reset_alert', methods=['POST'])
def reset_alert_status():
    """重置警报状态，避免重复提醒"""
    data = request.json
    if not data or 'stock_code' not in data or 'direction' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    stock_code = data['stock_code']
    direction = data['direction']
    
    success = reset_alert(stock_code, direction)
    
    if success:
        return jsonify({"message": "警报状态已重置"}), 200
    else:
        return jsonify({"error": "重置警报状态失败"}), 400

@app.route('/api/alert_log', methods=['GET'])
def get_alert_log():
    """获取历史告警日志"""
    try:
        # 获取查询参数
        user_email = request.args.get('user_email')
        stock_code = request.args.get('stock_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 限制页面大小
        if page_size > 100:
            page_size = 100
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 解析日期参数
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                return jsonify({"error": "start_date 格式错误，应为 YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS"}), 400
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                return jsonify({"error": "end_date 格式错误，应为 YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS"}), 400
        
        # 查询告警日志
        logs = get_alert_logs(
            user_email=user_email,
            stock_code=stock_code,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=page_size,
            offset=offset
        )
        
        # 获取总数用于分页
        total_count = get_alert_logs_count(
            user_email=user_email,
            stock_code=stock_code,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        # 计算分页信息
        total_pages = (total_count + page_size - 1) // page_size
        
        return jsonify({
            "success": True,
            "data": logs,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })
        
    except Exception as e:
        app.logger.error(f"获取告警日志出错: {e}")
        return jsonify({"error": "获取告警日志失败"}), 500

def monitor_job():
    """定时监控任务"""
    app.logger.info("执行定时监控任务")
    
    # 检查股票阈值
    alerts = check_thresholds()
    
    # 处理警报
    if alerts:
        app.logger.info(f"发现 {len(alerts)} 个股票价格警报")
        for alert in alerts:
            message = format_alert_message(alert)
            app.logger.warning(message)
            
            # TODO: 发送邮件通知用户
            # send_email(alert['user_email'], "股票价格预警", message)
    else:
        app.logger.info("没有发现股票价格警报")

def start_scheduler():
    """启动定时任务调度器"""
    if scheduler.running:
        return
    
    # 添加定时任务，每60秒执行一次
    scheduler.add_job(
        func=monitor_job,
        trigger=IntervalTrigger(seconds=60),
        id='monitor_job',
        name='股票价格监控',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    app.logger.info("股票价格监控定时任务已启动")

if __name__ == '__main__':
    # 启动定时任务
    start_scheduler()
    
    # 启动Flask应用
    app.run(debug=True, port=5000) 