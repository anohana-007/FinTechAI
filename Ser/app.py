import json
import logging
import threading
# 导入日志配置来修复Windows控制台编码问题
import logging_config
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from functools import wraps
from datetime import datetime, timedelta
from services.stock_service import get_stock_price, search_stocks, validate_tushare_token
from services.watchlist_service import get_watchlist, add_stock, remove_stock, update_stock_thresholds
from services.monitor_service import check_thresholds, format_alert_message, check_and_get_alerts
from services.alert_manager import reset_alert
from services.database_service import get_alert_logs, get_alert_logs_count, init_database
from services.auth_service import (
    init_user_database, register_user, authenticate_user, 
    get_user_by_id, get_user_config, get_user_config_summary, 
    get_user_config_for_editing, update_user_config, change_password
)
from services.ai_connectivity_service import test_ai_connectivity
from services.proxy_test_service import test_proxy_connectivity, validate_proxy_settings

# 初始化数据库
try:
    init_database()
    init_user_database()
    print("数据库初始化成功")
except Exception as e:
    print(f"数据库初始化失败: {e}")

app = Flask(__name__)

# 配置Flask会话
app.secret_key = 'fintech-ai-secret-key-2024-very-secure-and-long-for-testing'  # 项目使用数据库存储，使用固定的密钥
# 设置session过期时间为7天
app.permanent_session_lifetime = timedelta(days=7)
# 配置session cookie的属性
app.config.update(
    SESSION_COOKIE_SECURE=False,  # 开发环境设为False，生产环境应该设为True
    SESSION_COOKIE_HTTPONLY=True,  # 恢复为True以提高安全性
    SESSION_COOKIE_SAMESITE='Lax',  # 恢复为Lax，同域情况下更安全
    SESSION_COOKIE_DOMAIN=None,  # 不设置域，允许localhost工作
)

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
            
            app.logger.info(f"登录成功，设置会话 - user_id: {user_info['id']}, username: {user_info['username']}")
            app.logger.info(f"会话设置后的内容: {dict(session)}")
            app.logger.info(f"会话是否为permanent: {session.permanent}")
            app.logger.info(f"session.sid: {getattr(session, 'sid', 'No SID')}")
            
            # 创建响应并手动设置cookie以确保它被正确设置
            response = jsonify({
                "message": "登录成功",
                "user": {
                    "id": user_info['id'],
                    "username": user_info['username'],
                    "email": user_info['email']
                }
            })
            
            # 记录响应cookies
            app.logger.info("准备返回登录响应")
            
            return response, 200
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
    app.logger.info(f"收到check_session请求")
    app.logger.info(f"请求headers: {dict(request.headers)}")
    app.logger.info(f"请求cookies: {dict(request.cookies)}")
    app.logger.info(f"当前session内容: {dict(session)}")
    app.logger.info(f"session.sid: {getattr(session, 'sid', 'No SID')}")
    app.logger.info(f"会话中是否包含user_id: {'user_id' in session}")
    
    if 'user_id' in session:
        app.logger.info(f"从会话中获取user_id: {session.get('user_id')}")
        user_info = get_current_user()
        if user_info:
            app.logger.info(f"成功获取用户信息: {user_info}")
            return jsonify({
                "authenticated": True,
                "user": user_info
            }), 200
        else:
            app.logger.warning("会话中有user_id但无法获取用户信息")
    else:
        app.logger.info("会话中没有user_id，用户未认证")
    
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

@app.route('/auth/session_info', methods=['GET'])
def session_info():
    """显示会话配置信息（仅用于调试）"""
    info = {
        'session_config': {
            'SECRET_KEY_LENGTH': len(app.secret_key),
            'SESSION_COOKIE_SECURE': app.config.get('SESSION_COOKIE_SECURE'),
            'SESSION_COOKIE_HTTPONLY': app.config.get('SESSION_COOKIE_HTTPONLY'),
            'SESSION_COOKIE_SAMESITE': app.config.get('SESSION_COOKIE_SAMESITE'),
            'SESSION_COOKIE_DOMAIN': app.config.get('SESSION_COOKIE_DOMAIN'),
            'PERMANENT_SESSION_LIFETIME': str(app.permanent_session_lifetime),
        },
        'current_session': dict(session),
        'session_permanent': session.permanent,
        'request_cookies': dict(request.cookies)
    }
    return jsonify(info), 200

# ========== 用户设置API ==========

@app.route('/api/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    """获取用户设置"""
    try:
        # 获取查询参数，判断是获取摘要还是详细信息
        detail = request.args.get('detail', 'false').lower() == 'true'
        
        if detail:
            # 获取详细配置信息用于编辑
            config_detail = get_user_config_for_editing(session['user_id'])
            if config_detail:
                return jsonify({
                    "success": True,
                    "settings": config_detail
                }), 200
            else:
                return jsonify({"error": "获取用户设置失败"}), 500
        else:
            # 获取配置摘要
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
        
        # 处理AI配置（新的详细配置结构）
        if 'ai_configurations' in data and isinstance(data['ai_configurations'], dict):
            config_data['ai_configurations'] = data['ai_configurations']
        
        # 处理代理设置
        if 'proxy_settings' in data and isinstance(data['proxy_settings'], dict):
            config_data['proxy_settings'] = data['proxy_settings']
        
        if 'preferred_llm' in data:
            config_data['preferred_llm'] = data['preferred_llm'].strip() if data['preferred_llm'] else 'openai'
        
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
@login_required
def watchlist():
    """获取用户关注的股票列表，包含实时价格"""
    try:
        app.logger.info("开始获取用户关注列表和实时价格...")
        
        # 获取基础关注列表
        stocks = get_watchlist()
        app.logger.info(f"从文件获取到 {len(stocks)} 只股票")
        
        if not stocks:
            app.logger.info("关注列表为空")
            return jsonify([])
        
        # 获取当前用户配置（用于股价获取）
        user_config = get_current_user_config()
        if not user_config:
            app.logger.warning("无法获取用户配置，将返回不含价格的列表")
            return jsonify(stocks)
        
        app.logger.info("开始获取实时股票价格...")
        
        # 为每只股票获取实时价格
        updated_stocks = []
        for stock in stocks:
            stock_code = stock.get('stock_code')
            app.logger.info(f"获取股票 {stock_code} 的实时价格...")
            
            try:
                from services.stock_service import get_stock_price
                current_price = get_stock_price(stock_code, user_config)
                
                # 更新股票信息
                updated_stock = stock.copy()
                updated_stock['current_price'] = current_price
                
                if current_price:
                    app.logger.info(f"  [成功] {stock_code} 当前价格: ¥{current_price}")
                else:
                    app.logger.warning(f"  [失败] {stock_code} 无法获取价格")
                
                updated_stocks.append(updated_stock)
                
            except Exception as e:
                app.logger.error(f"获取股票 {stock_code} 价格时出错: {e}")
                # 即使获取价格失败，也添加到列表中（价格为None）
                updated_stock = stock.copy()
                updated_stock['current_price'] = None
                updated_stocks.append(updated_stock)
        
        app.logger.info(f"成功返回 {len(updated_stocks)} 只股票的信息")
        return jsonify(updated_stocks)
        
    except Exception as e:
        app.logger.error(f"获取关注列表时出错: {e}")
        return jsonify({"error": "获取关注列表失败，请稍后重试"}), 500

@app.route('/api/add_stock', methods=['POST'])
def add_stock_to_watchlist():
    """添加股票到关注列表"""
    try:
        app.logger.info("=== 开始添加股票到关注列表 ===")
        
        data = request.json
        app.logger.info(f"接收到的请求数据: {data}")
        
        if not data:
            app.logger.error("请求数据为空")
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 验证必要字段
        required_fields = ['stock_code', 'stock_name', 'upper_threshold', 'lower_threshold', 'user_email']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            app.logger.error(f"缺少必要字段: {missing_fields}")
            return jsonify({"error": f"缺少必要字段: {', '.join(missing_fields)}"}), 400
        
        app.logger.info("必要字段验证通过")
        
        # 记录详细的字段信息
        app.logger.info(f"股票代码: {data['stock_code']}")
        app.logger.info(f"股票名称: {data['stock_name']}")
        app.logger.info(f"上限阈值: {data['upper_threshold']} (类型: {type(data['upper_threshold'])})")
        app.logger.info(f"下限阈值: {data['lower_threshold']} (类型: {type(data['lower_threshold'])})")
        app.logger.info(f"用户邮箱: {data['user_email']}")
        
        # 添加股票到关注列表
        app.logger.info("调用add_stock函数...")
        success, message = add_stock(data)
        
        app.logger.info(f"add_stock结果: success={success}, message={message}")
        
        if success:
            app.logger.info("股票添加成功!")
            return jsonify({"message": message}), 201
        else:
            app.logger.warning(f"股票添加失败: {message}")
            return jsonify({"error": message}), 400
            
    except Exception as e:
        app.logger.error(f"添加股票时发生异常: {e}")
        app.logger.error("=== 添加股票异常结束 ===")
        return jsonify({"error": "服务器内部错误，请稍后重试"}), 500

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
    try:
        # 首先尝试从数据库获取最近10分钟的告警日志
        from datetime import datetime, timedelta
        from services.database_service import get_alert_logs
        
        # 获取最近10分钟的告警
        recent_time = datetime.now() - timedelta(minutes=10)
        recent_alerts = get_alert_logs(
            start_date=recent_time,
            limit=10,  # 最多返回10条
            offset=0
        )
        
        # 转换数据库告警为API格式
        formatted_alerts = []
        for alert in recent_alerts:
            formatted_alert = {
                'stock_code': alert['stock_code'],
                'stock_name': alert['stock_name'],
                'current_price': alert['triggered_price'],
                'threshold': alert['threshold_price'],
                'direction': alert['direction'],
                'timestamp': alert['alert_timestamp'],
                'message': format_alert_message({
                    'stock_code': alert['stock_code'],
                    'stock_name': alert['stock_name'],
                    'current_price': alert['triggered_price'],
                    'threshold': alert['threshold_price'],
                    'direction': alert['direction'],
                    'timestamp': alert['alert_timestamp']
                }),
                'ai_analysis': alert.get('ai_analysis', '')
            }
            formatted_alerts.append(formatted_alert)
        
        # 如果数据库中没有最近的告警，使用原有的检查逻辑作为后备
        if not formatted_alerts:
            alerts = check_and_get_alerts()
            
            for alert in alerts:
                # 确保字段名称一致 - 兼容不同的字段名
                current_price = alert.get('current_price') or alert.get('price') or alert.get('triggered_price')
                threshold = alert.get('threshold') or alert.get('threshold_price')
                
                formatted_alert = {
                    'stock_code': alert['stock_code'],
                    'stock_name': alert.get('stock_name', '未知股票'),
                    'current_price': current_price,
                    'threshold': threshold,
                    'direction': alert['direction'],
                    'timestamp': alert.get('timestamp'),
                    'message': format_alert_message({
                        **alert,
                        'current_price': current_price,
                        'threshold': threshold
                    }),
                    'ai_analysis': alert.get('ai_analysis', '')
                }
                formatted_alerts.append(formatted_alert)
        
        return jsonify({
            "has_alerts": len(formatted_alerts) > 0,
            "alerts": formatted_alerts
        })
        
    except Exception as e:
        app.logger.error(f"检查告警状态失败: {e}")
        # 发生错误时，返回空的告警列表
        return jsonify({
            "has_alerts": False,
            "alerts": []
        })

@app.route('/api/analyze_stock_manually', methods=['POST'])
@login_required
def analyze_stock_manually():
    """手动分析股票"""
    try:
        app.logger.info("=== 开始手动股票AI分析 ===")
        
        data = request.json
        if not data:
            app.logger.error("请求数据为空")
            return jsonify({"error": "无效的请求数据"}), 400
        
        stock_code = data.get('stock_code', '').strip()
        llm_preference = data.get('llm_preference', '').strip().lower()
        
        app.logger.info(f"请求参数: stock_code={stock_code}, llm_preference={llm_preference}")
        
        if not stock_code:
            app.logger.error("股票代码为空")
            return jsonify({"error": "股票代码不能为空"}), 400
        
        # 获取用户配置
        user_config = get_current_user_config()
        if not user_config:
            app.logger.error("无法获取用户配置")
            return jsonify({"error": "用户配置获取失败"}), 401
        
        app.logger.info("[成功] 用户配置获取成功")
        
        # 如果没有指定LLM偏好，使用用户配置的默认值
        if not llm_preference:
            llm_preference = user_config.get('preferred_llm', 'openai')
            app.logger.info(f"使用用户默认LLM偏好: {llm_preference}")
        
        # 验证LLM偏好
        valid_llms = ['openai', 'gemini', 'deepseek', 'google']  # 添加google支持
        if llm_preference not in valid_llms:
            app.logger.error(f"不支持的LLM类型: {llm_preference}")
            return jsonify({"error": f"不支持的LLM类型: {llm_preference}。支持的类型: {', '.join(valid_llms)}"}), 400
        
        app.logger.info(f"[成功] LLM偏好验证通过: {llm_preference}")
        
        # 检查AI配置
        ai_configurations = user_config.get('ai_configurations', {})
        app.logger.info(f"用户AI配置数量: {len(ai_configurations)}")
        
        # 显示AI配置详情
        for provider_id, config in ai_configurations.items():
            enabled = config.get('enabled', False)
            has_key = bool(config.get('api_key'))
            app.logger.info(f"  - {provider_id}: {'启用' if enabled else '禁用'}, {'有密钥' if has_key else '无密钥'}")
        
        # 获取股票当前价格
        app.logger.info(f"开始获取股票 {stock_code} 的当前价格...")
        
        from services.stock_service import get_stock_price
        current_price = get_stock_price(stock_code, user_config)
        
        if current_price is None:
            app.logger.error(f"无法获取股票 {stock_code} 的价格")
            return jsonify({"error": "无法获取股票价格，请检查股票代码是否正确"}), 404
        
        app.logger.info(f"[成功] 股票价格获取成功: ¥{current_price}")
        
        # 调用AI分析服务
        app.logger.info(f"开始调用AI分析服务: {llm_preference}")
        
        from services.ai_analysis_service import get_ai_analysis
        analysis_result = get_ai_analysis(
            stock_code=stock_code,
            current_price=current_price,
            llm_preference=llm_preference,
            user_config=user_config
        )
        
        app.logger.info(f"AI分析服务调用完成")
        
        # 检查分析结果
        if analysis_result.get('error'):
            app.logger.error(f"AI分析失败: {analysis_result.get('message')}")
            app.logger.error(f"详细错误: {analysis_result}")
            return jsonify({
                "error": analysis_result.get('message', 'AI分析失败'),
                "details": analysis_result
            }), 500
        
        # 返回成功结果
        response_data = {
            "success": True,
            "stock_code": stock_code,
            "current_price": current_price,
            "llm_used": analysis_result.get('provider', llm_preference),
            "analysis": analysis_result
        }
        
        app.logger.info(f"[完成] 手动股票分析成功完成!")
        app.logger.info(f"  - 股票: {stock_code}")
        app.logger.info(f"  - 价格: ¥{current_price}")
        app.logger.info(f"  - LLM: {analysis_result.get('provider', llm_preference)}")
        app.logger.info(f"  - 评分: {analysis_result.get('overall_score')}")
        app.logger.info(f"  - 建议: {analysis_result.get('recommendation')}")
        app.logger.info("=== 手动股票AI分析结束 ===")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.error(f"手动股票分析出错: {e}")
        app.logger.error("=== 手动股票AI分析异常结束 ===")
        return jsonify({"error": "股票分析失败，请稍后重试"}), 500

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

@app.route('/api/test_ai_connectivity', methods=['POST'])
@login_required
def test_ai_connectivity_endpoint():
    """测试AI服务连通性"""
    try:
        app.logger.info("=== 开始AI连通性测试 ===")
        
        data = request.json
        if not data:
            app.logger.error("请求数据为空")
            return jsonify({"error": "无效的请求数据"}), 400
        
        provider = data.get('provider', '').strip()
        model = data.get('model', '').strip()
        base_url = data.get('base_url', '').strip()
        api_key = data.get('api_key', '').strip()
        
        app.logger.info(f"连通性测试参数: provider={provider}, model={model}, base_url={base_url}")
        
        if not all([provider, model, api_key]):
            app.logger.error(f"缺少必要参数: provider={bool(provider)}, model={bool(model)}, api_key={bool(api_key)}")
            return jsonify({"error": "缺少必要参数：provider, model, api_key"}), 400
        
        # 强制刷新用户配置，确保获取最新数据
        app.logger.info(f"强制刷新用户配置: user_id={session['user_id']}")
        
        # 等待一小段时间确保数据库同步（如果刚刚更新过配置）
        import time
        time.sleep(0.05)
        
        # 获取用户的代理设置
        user_config = get_current_user_config()
        if user_config:
            app.logger.info("成功获取用户配置")
            
            # 详细记录用户的AI配置状态
            ai_configurations = user_config.get('ai_configurations', {})
            app.logger.info(f"用户AI配置: {len(ai_configurations)} 个提供商")
            
            for provider_id, config in ai_configurations.items():
                has_api_key = bool(config.get('api_key'))
                model_id = config.get('model_id', 'N/A')
                enabled = config.get('enabled', False)
                app.logger.info(f"  {provider_id}: 模型={model_id}, 启用={enabled}, 有密钥={has_api_key}")
            
            proxy_settings = user_config.get('proxy_settings', {})
            if proxy_settings and proxy_settings.get('enabled'):
                proxy_host = proxy_settings.get('host', 'N/A')
                app.logger.info(f"使用代理设置: {proxy_host}")
            else:
                app.logger.info("未启用代理")
        else:
            app.logger.warning("无法获取用户配置，将使用空代理设置")
            proxy_settings = {}
        
        proxy_settings = user_config.get('proxy_settings', {}) if user_config else {}
        
        app.logger.info("开始执行连通性测试...")
        
        # 执行连通性测试
        result = test_ai_connectivity(
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key,
            proxy_settings=proxy_settings
        )
        
        app.logger.info(f"连通性测试完成: 成功={result.get('success', False)}")
        if not result.get('success'):
            app.logger.error(f"测试失败原因: {result.get('error', 'Unknown')}")
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"AI连通性测试出错: {e}", exc_info=True)
        return jsonify({"error": "连通性测试失败，请稍后重试"}), 500

@app.route('/api/ai_providers', methods=['GET'])
def get_ai_providers():
    """获取可用的AI服务提供商和模型列表"""
    try:
        providers = {
            'openai': {
                'name': 'OpenAI',
                'description': 'OpenAI提供的GPT系列模型',
                'default_base_url': 'https://api.openai.com/v1/chat/completions',
                'models': [
                    {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': '快速、高效的对话模型'},
                    {'id': 'gpt-4', 'name': 'GPT-4', 'description': '更强大的多模态模型'},
                    {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'GPT-4的优化版本'},
                    {'id': 'gpt-4o', 'name': 'GPT-4o', 'description': '最新的GPT-4模型'}
                ]
            },
            'deepseek': {
                'name': 'DeepSeek',
                'description': 'DeepSeek提供的代码和对话模型',
                'default_base_url': 'https://api.deepseek.com/v1/chat/completions',
                'models': [
                    {'id': 'deepseek-chat', 'name': 'DeepSeek Chat', 'description': '通用对话模型'},
                    {'id': 'deepseek-coder', 'name': 'DeepSeek Coder', 'description': '专业代码模型'}
                ]
            },
            'google': {
                'name': 'Google',
                'description': 'Google提供的Gemini系列模型',
                'default_base_url': 'https://generativelanguage.googleapis.com/v1beta/models/',
                'models': [
                    {'id': 'gemini-pro', 'name': 'Gemini Pro', 'description': '高性能多模态模型'},
                    {'id': 'gemini-pro-vision', 'name': 'Gemini Pro Vision', 'description': '支持图像理解的模型'},
                    {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': '最新版本的Gemini Pro'},
                    {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'description': '快速响应版本'}
                ]
            },
            'anthropic': {
                'name': 'Anthropic',
                'description': 'Anthropic提供的Claude系列模型',
                'default_base_url': 'https://api.anthropic.com/v1/messages',
                'models': [
                    {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku', 'description': '快速、轻量级模型'},
                    {'id': 'claude-3-sonnet-20240229', 'name': 'Claude 3 Sonnet', 'description': '平衡性能和速度'},
                    {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus', 'description': '最强大的Claude模型'}
                ]
            },
            'custom': {
                'name': '自定义API',
                'description': '自定义的AI API服务',
                'default_base_url': '',
                'models': [
                    {'id': 'custom-model', 'name': '自定义模型', 'description': '用户自定义的AI模型'}
                ]
            }
        }
        
        return jsonify(providers), 200
        
    except Exception as e:
        app.logger.error(f"获取AI提供商列表出错: {e}")
        return jsonify({"error": "获取提供商列表失败"}), 500

@app.route('/api/test_proxy_connectivity', methods=['POST'])
@login_required
def test_proxy_connectivity_endpoint():
    """测试代理连通性"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 解析代理设置 - 前端发送的数据格式为 { proxy_settings: {...} }
        proxy_settings = data.get('proxy_settings', {})
        
        # 执行代理连通性测试
        result = test_proxy_connectivity(proxy_settings)
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"代理连通性测试出错: {e}")
        return jsonify({"error": "代理连通性测试失败，请稍后重试"}), 500

@app.route('/api/validate_proxy_settings', methods=['POST'])
@login_required
def validate_proxy_settings_endpoint():
    """验证代理设置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 解析代理设置
        proxy_settings = data.get('proxy_settings', {})
        
        # 执行代理设置验证
        result = validate_proxy_settings(proxy_settings)
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"代理设置验证出错: {e}")
        return jsonify({"error": "代理设置验证失败，请稍后重试"}), 500

@app.route('/api/validate_tushare_token', methods=['POST'])
@login_required
def validate_tushare_token_endpoint():
    """验证Tushare Token有效性"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        token = data.get('token', '').strip()
        if not token:
            return jsonify({"error": "Token不能为空"}), 400
        
        # 获取用户配置（包含代理设置）
        user_config = get_current_user_config()
        
        # 执行验证
        result = validate_tushare_token(token, user_config)
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"验证Tushare Token出错: {e}")
        return jsonify({
            "valid": False,
            "message": "Token验证失败",
            "details": {"error": str(e)}
        }), 500

if __name__ == '__main__':
    # 启动定时任务
    start_scheduler()
    
    # 启动Flask应用 - 使用localhost而不是127.0.0.1以匹配前端域名
    app.run(debug=True, host='localhost', port=5000) 