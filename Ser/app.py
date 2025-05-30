import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.stock_service import get_stock_price
from services.watchlist_service import get_watchlist, add_stock
from services.monitor_service import check_thresholds, format_alert_message, check_and_get_alerts
from services.alert_manager import reset_alert

# 加载环境变量
load_dotenv()
print(f"环境变量TUSHARE_TOKEN: {'已设置' if os.getenv('TUSHARE_TOKEN') else '未设置'}")

app = Flask(__name__)

# 配置CORS，允许前端跨域请求
CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:3000",  # 允许的前端源
        "methods": ["GET", "POST", "OPTIONS"],  # 允许的HTTP方法
        "allow_headers": ["Content-Type", "Authorization"],  # 允许的请求头
        "supports_credentials": True  # 允许携带凭证(cookies)
    }
})

# 创建调度器
scheduler = BackgroundScheduler()

@app.route('/api/stock_price/<stock_code>')
def stock_price(stock_code):
    """获取指定股票代码的当前价格"""
    price = get_stock_price(stock_code)
    if price is None:
        return jsonify({"error": "无法获取股票价格"}), 404
    return jsonify({
        "code": stock_code,
        "price": price
    })

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