import time
import logging
import os
from datetime import datetime
from .stock_service import get_stock_price
from .watchlist_service import get_watchlist
from .email_service import send_email_alert, format_stock_alert_email
from .ai_analysis_service import get_basic_ai_analysis
from .alert_manager import is_new_alert, get_recent_alerts

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("monitor_service")

# 是否发送邮件提醒
ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true'

# 是否启用AI分析
ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'False').lower() == 'true'

def check_thresholds():
    """
    检查所有关注股票的价格是否突破阈值
    
    返回:
    list: 突破阈值的股票记录列表
    """
    logger.info("开始检查股票阈值...")
    
    # 读取关注列表
    watchlist = get_watchlist()
    if not watchlist:
        logger.info("关注列表为空，无需检查")
        return []
    
    # 记录突破阈值的股票
    alerts = []
    
    # 遍历关注列表
    for stock in watchlist:
        stock_code = stock.get('stock_code')
        stock_name = stock.get('stock_name')
        upper_threshold = float(stock.get('upper_threshold'))
        lower_threshold = float(stock.get('lower_threshold'))
        user_email = stock.get('user_email')
        
        logger.info(f"检查股票: {stock_code} ({stock_name})")
        
        # 获取当前股价
        current_price = get_stock_price(stock_code)
        
        # 如果无法获取价格，跳过
        if current_price is None:
            logger.warning(f"无法获取股票 {stock_code} 的价格，跳过检查")
            continue
        
        logger.info(f"当前价格: {current_price}, 上限: {upper_threshold}, 下限: {lower_threshold}")
        
        # 检查是否突破上限
        if current_price >= upper_threshold:
            logger.warning(f"股票 {stock_code} ({stock_name}) 价格 {current_price} 突破上限 {upper_threshold}")
            
            # 创建警报对象
            alert = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': current_price,
                'threshold': upper_threshold,
                'direction': 'UP',
                'user_email': user_email,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 检查是否是新警报
            if is_new_alert(stock_code, 'UP', current_price, upper_threshold):
                # 添加AI分析
                if ENABLE_AI_ANALYSIS:
                    try:
                        ai_analysis = get_basic_ai_analysis(stock_code, current_price, 'UP')
                        alert['ai_analysis'] = ai_analysis
                    except Exception as e:
                        logger.error(f"获取AI分析时出错: {e}")
                        alert['ai_analysis'] = "AI分析暂不可用"
                
                # 添加到警报列表
                alerts.append(alert)
                
                # 发送邮件提醒
                if ENABLE_EMAIL_ALERTS and user_email:
                    send_alert_email(alert)
        
        # 检查是否突破下限
        elif current_price <= lower_threshold:
            logger.warning(f"股票 {stock_code} ({stock_name}) 价格 {current_price} 突破下限 {lower_threshold}")
            
            # 创建警报对象
            alert = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': current_price,
                'threshold': lower_threshold,
                'direction': 'DOWN',
                'user_email': user_email,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 检查是否是新警报
            if is_new_alert(stock_code, 'DOWN', current_price, lower_threshold):
                # 添加AI分析
                if ENABLE_AI_ANALYSIS:
                    try:
                        ai_analysis = get_basic_ai_analysis(stock_code, current_price, 'DOWN')
                        alert['ai_analysis'] = ai_analysis
                    except Exception as e:
                        logger.error(f"获取AI分析时出错: {e}")
                        alert['ai_analysis'] = "AI分析暂不可用"
                
                # 添加到警报列表
                alerts.append(alert)
                
                # 发送邮件提醒
                if ENABLE_EMAIL_ALERTS and user_email:
                    send_alert_email(alert)
        
        # 避免频繁请求API，添加短暂延迟
        time.sleep(0.5)
    
    logger.info(f"检查完成，发现 {len(alerts)} 个突破阈值的股票")
    return alerts

def send_alert_email(alert):
    """
    发送股票价格提醒邮件
    
    参数:
    alert (dict): 警报信息
    """
    try:
        user_email = alert['user_email']
        if not user_email:
            logger.warning("用户邮箱为空，无法发送提醒")
            return False
        
        # 获取AI分析结果
        ai_analysis = alert.get('ai_analysis')
        
        # 格式化邮件内容
        subject, body = format_stock_alert_email(alert, ai_analysis)
        
        # 发送邮件
        success = send_email_alert(user_email, subject, body)
        
        if success:
            logger.info(f"成功发送价格提醒至 {user_email}")
        else:
            logger.error(f"发送价格提醒至 {user_email} 失败")
        
        return success
    except Exception as e:
        logger.error(f"发送提醒邮件时出错: {e}")
        return False

def check_and_get_alerts():
    """
    检查股票价格并返回警报信息（用于API端点）
    
    返回:
    list: 警报列表，包含AI分析
    """
    # 执行检查，获取新警报
    new_alerts = check_thresholds()
    
    # 如果没有新警报，获取最近的警报
    if not new_alerts:
        recent_alerts = get_recent_alerts(minutes=10)
        
        # 为最近的警报添加更多信息
        for alert in recent_alerts:
            # 添加股票名称
            watchlist = get_watchlist()
            for stock in watchlist:
                if stock.get('stock_code') == alert['stock_code']:
                    alert['stock_name'] = stock.get('stock_name')
                    alert['user_email'] = stock.get('user_email')
                    break
            
            # 添加AI分析（如果启用）
            if ENABLE_AI_ANALYSIS and 'ai_analysis' not in alert:
                try:
                    ai_analysis = get_basic_ai_analysis(
                        alert['stock_code'], 
                        alert['price'], 
                        alert['direction']
                    )
                    alert['ai_analysis'] = ai_analysis
                except Exception as e:
                    logger.error(f"获取AI分析时出错: {e}")
                    alert['ai_analysis'] = "AI分析暂不可用"
        
        return recent_alerts
    
    return new_alerts

def format_alert_message(alert):
    """
    格式化警报消息
    
    参数:
    alert (dict): 警报信息
    
    返回:
    str: 格式化后的消息
    """
    direction = "上涨" if alert['direction'] == 'UP' else "下跌"
    
    # 基本信息
    message = (
        f"股票价格预警: {alert['stock_name']}({alert['stock_code']})\n"
        f"当前价格: {alert['current_price']} 已{direction}至阈值 {alert['threshold']}\n"
        f"触发时间: {alert['timestamp']}"
    )
    
    # 添加AI分析（如果有）
    if 'ai_analysis' in alert and alert['ai_analysis']:
        message += f"\n\nAI分析: {alert['ai_analysis']}"
    
    return message 