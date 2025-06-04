import time
import logging
import os
from datetime import datetime
from .stock_service import get_stock_price
from .watchlist_service import get_watchlist
from .email_service import send_email_alert, format_stock_alert_email
from .ai_analysis_service import get_basic_ai_analysis
from .alert_manager import is_new_alert, get_recent_alerts
from .database_service import save_alert_log, init_database
from .auth_service import get_user_config, get_user_config_by_email

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

# 配置开关
ENABLE_EMAIL_ALERTS = True  # 是否启用邮件提醒
ENABLE_AI_ANALYSIS = True  # 是否启用AI分析

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
        
        # 获取用户配置（用于AI分析和股价获取）
        user_config = get_user_config_by_email(user_email) if user_email else None
        
        # 获取当前股价
        current_price = get_stock_price(stock_code, user_config)
        
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
                if ENABLE_AI_ANALYSIS and 'ai_analysis' not in alert:
                    try:
                        # 获取用户配置
                        user_config = get_user_config_by_email(alert.get('user_email')) if alert.get('user_email') else None
                        # 使用结构化AI分析函数
                        from .ai_analysis_service import get_ai_analysis
                        ai_analysis_result = get_ai_analysis(
                            alert['stock_code'], 
                            alert.get('triggered_price', alert.get('current_price', 0)), 
                            'openai',  # 默认使用openai，也可以从用户配置读取
                            user_config,
                            {'breakout_direction': 'UP', 'stock_name': alert.get('stock_name', '未知')}
                        )
                        
                        # 如果AI分析成功，保存完整的结构化结果
                        if ai_analysis_result and not ai_analysis_result.get('error'):
                            alert['ai_analysis'] = ai_analysis_result
                        else:
                            # 如果AI分析失败，保存错误信息的简化版本
                            alert['ai_analysis'] = ai_analysis_result.get('message', 'AI分析暂不可用')
                    except Exception as e:
                        logger.error(f"获取AI分析时出错: {e}")
                        alert['ai_analysis'] = "AI分析暂不可用"
                
                # 保存到数据库
                try:
                    # 处理AI分析数据，如果是结构化数据则转换为JSON字符串
                    ai_analysis_for_db = alert.get('ai_analysis', '')
                    if isinstance(ai_analysis_for_db, dict):
                        import json
                        ai_analysis_for_db = json.dumps(ai_analysis_for_db, ensure_ascii=False)
                    
                    alert_data = {
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'triggered_price': current_price,
                        'threshold_price': upper_threshold,
                        'direction': 'UP',
                        'ai_analysis': ai_analysis_for_db,
                        'user_email': user_email,
                        'alert_timestamp': datetime.now()
                    }
                    save_alert_log(alert_data)
                except Exception as e:
                    logger.error(f"保存告警日志到数据库失败: {e}")
                
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
                if ENABLE_AI_ANALYSIS and 'ai_analysis' not in alert:
                    try:
                        # 获取用户配置
                        user_config = get_user_config_by_email(alert.get('user_email')) if alert.get('user_email') else None
                        # 使用结构化AI分析函数
                        from .ai_analysis_service import get_ai_analysis
                        ai_analysis_result = get_ai_analysis(
                            alert['stock_code'], 
                            alert.get('triggered_price', alert.get('current_price', 0)), 
                            'openai',  # 默认使用openai，也可以从用户配置读取
                            user_config,
                            {'breakout_direction': 'DOWN', 'stock_name': alert.get('stock_name', '未知')}
                        )
                        
                        # 如果AI分析成功，保存完整的结构化结果
                        if ai_analysis_result and not ai_analysis_result.get('error'):
                            alert['ai_analysis'] = ai_analysis_result
                        else:
                            # 如果AI分析失败，保存错误信息的简化版本
                            alert['ai_analysis'] = ai_analysis_result.get('message', 'AI分析暂不可用')
                    except Exception as e:
                        logger.error(f"获取AI分析时出错: {e}")
                        alert['ai_analysis'] = "AI分析暂不可用"
                
                # 保存到数据库
                try:
                    # 处理AI分析数据，如果是结构化数据则转换为JSON字符串
                    ai_analysis_for_db = alert.get('ai_analysis', '')
                    if isinstance(ai_analysis_for_db, dict):
                        import json
                        ai_analysis_for_db = json.dumps(ai_analysis_for_db, ensure_ascii=False)
                    
                    alert_data = {
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'triggered_price': current_price,
                        'threshold_price': lower_threshold,
                        'direction': 'DOWN',
                        'ai_analysis': ai_analysis_for_db,
                        'user_email': user_email,
                        'alert_timestamp': datetime.now()
                    }
                    save_alert_log(alert_data)
                except Exception as e:
                    logger.error(f"保存告警日志到数据库失败: {e}")
                
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
                    # 获取用户配置
                    user_config = get_user_config_by_email(alert.get('user_email')) if alert.get('user_email') else None
                    # 使用结构化AI分析函数
                    from .ai_analysis_service import get_ai_analysis
                    ai_analysis_result = get_ai_analysis(
                        alert['stock_code'], 
                        alert.get('triggered_price', alert.get('current_price', 0)), 
                        'openai',  # 默认使用openai，也可以从用户配置读取
                        user_config,
                        {'breakout_direction': alert['direction'], 'stock_name': alert.get('stock_name', '未知')}
                    )
                    
                    # 如果AI分析成功，保存完整的结构化结果
                    if ai_analysis_result and not ai_analysis_result.get('error'):
                        alert['ai_analysis'] = ai_analysis_result
                    else:
                        # 如果AI分析失败，保存错误信息的简化版本
                        alert['ai_analysis'] = ai_analysis_result.get('message', 'AI分析暂不可用')
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
    
    # 处理时间戳格式
    timestamp = alert.get('timestamp')
    if timestamp:
        # 如果是datetime对象，转换为字符串
        if hasattr(timestamp, 'strftime'):
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # 如果是ISO格式字符串，尝试转换
        elif isinstance(timestamp, str) and 'T' in timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass  # 保持原始格式
    else:
        timestamp = "未知时间"
    
    # 基本信息
    message = (
        f"股票价格预警: {alert['stock_name']}({alert['stock_code']})\n"
        f"当前价格: {alert['current_price']} 已{direction}至阈值 {alert['threshold']}\n"
        f"触发时间: {timestamp}"
    )
    
    # 添加AI分析（如果有）
    ai_analysis = alert.get('ai_analysis')
    if ai_analysis:
        # 如果AI分析是结构化数据，提取关键信息
        if isinstance(ai_analysis, dict):
            if ai_analysis.get('technical_summary'):
                message += f"\n\nAI技术分析: {ai_analysis['technical_summary']}"
            if ai_analysis.get('recommendation'):
                message += f"\n投资建议: {ai_analysis['recommendation']}"
            if ai_analysis.get('overall_score'):
                message += f"\nAI评分: {ai_analysis['overall_score']}/100"
        else:
            # 文本格式的AI分析
            message += f"\n\nAI分析: {ai_analysis}"
    
    return message 