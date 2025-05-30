import os
import json
import logging
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger('alert_manager')

# 警报状态文件路径
ALERTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'alerts_status.json')

def load_alerts_status():
    """
    加载警报状态记录
    
    返回:
    dict: 警报状态记录
    """
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"加载警报状态记录出错: {e}")
        return {}

def save_alerts_status(alerts_status):
    """
    保存警报状态记录
    
    参数:
    alerts_status (dict): 警报状态记录
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
        
        with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(alerts_status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存警报状态记录出错: {e}")

def is_new_alert(stock_code, direction, current_price, threshold, cooldown_minutes=60):
    """
    判断是否是新警报（避免重复提醒）
    
    参数:
    stock_code (str): 股票代码
    direction (str): 突破方向 ('UP' 或 'DOWN')
    current_price (float): 当前价格
    threshold (float): 阈值价格
    cooldown_minutes (int): 冷却时间（分钟）
    
    返回:
    bool: 是否是新警报
    """
    # 加载警报状态记录
    alerts_status = load_alerts_status()
    
    # 生成警报的唯一标识
    alert_key = f"{stock_code}_{direction}"
    
    # 当前时间
    now = datetime.now()
    
    # 如果此警报之前已记录
    if alert_key in alerts_status:
        last_alert = alerts_status[alert_key]
        
        # 解析上次警报时间
        last_time = datetime.fromisoformat(last_alert['timestamp'])
        
        # 判断是否在冷却期内
        if now - last_time < timedelta(minutes=cooldown_minutes):
            # 在冷却期内，如果价格变化不大，则不是新警报
            last_price = float(last_alert['price'])
            price_change_percent = abs(current_price - last_price) / last_price * 100
            
            # 如果价格变化超过2%，则视为新警报
            if price_change_percent < 2.0:
                return False
    
    # 更新警报状态
    alerts_status[alert_key] = {
        'timestamp': now.isoformat(),
        'price': str(current_price),
        'threshold': str(threshold),
        'notified': True
    }
    
    # 保存更新后的状态
    save_alerts_status(alerts_status)
    
    # 是新警报
    return True

def get_recent_alerts(minutes=10):
    """
    获取最近的警报
    
    参数:
    minutes (int): 获取多少分钟内的警报
    
    返回:
    list: 警报列表
    """
    alerts_status = load_alerts_status()
    now = datetime.now()
    recent_alerts = []
    
    for key, alert in alerts_status.items():
        try:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if now - alert_time <= timedelta(minutes=minutes):
                # 解析警报键，格式为 "stock_code_direction"
                parts = key.split('_')
                if len(parts) >= 2:
                    stock_code = parts[0]
                    direction = parts[1]
                    
                    recent_alerts.append({
                        'stock_code': stock_code,
                        'direction': direction,
                        'price': float(alert['price']),
                        'threshold': float(alert['threshold']),
                        'timestamp': alert['timestamp']
                    })
        except Exception as e:
            logger.error(f"处理警报记录时出错: {e}")
    
    return recent_alerts

def reset_alert(stock_code, direction):
    """
    重置特定股票的警报状态
    
    参数:
    stock_code (str): 股票代码
    direction (str): 突破方向 ('UP' 或 'DOWN')
    
    返回:
    bool: 是否成功重置
    """
    try:
        alerts_status = load_alerts_status()
        alert_key = f"{stock_code}_{direction}"
        
        if alert_key in alerts_status:
            del alerts_status[alert_key]
            save_alerts_status(alerts_status)
            return True
        return False
    except Exception as e:
        logger.error(f"重置警报状态时出错: {e}")
        return False 