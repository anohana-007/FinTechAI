"""
使用简单循环实现的定时监控服务
"""
import time
import logging
from datetime import datetime
from services.monitor_service import check_thresholds, format_alert_message

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_scheduler")

def monitor_job():
    """定时监控任务"""
    logger.info(f"执行定时监控任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查股票阈值
    alerts = check_thresholds()
    
    # 处理警报（这里只是打印，实际应用中可以发送邮件等）
    if alerts:
        logger.info(f"发现 {len(alerts)} 个股票价格警报")
        for alert in alerts:
            # 格式化警报消息
            message = format_alert_message(alert)
            logger.warning(message)
            
            # TODO: 发送邮件通知用户
            # send_email(alert['user_email'], "股票价格预警", message)
    else:
        logger.info("没有发现股票价格警报")

def start_simple_scheduler(interval=60):
    """
    启动简单的定时循环
    
    参数:
    interval (int): 检查间隔，单位为秒
    """
    logger.info(f"启动简单定时循环，检查间隔为 {interval} 秒...")
    
    try:
        while True:
            # 执行监控任务
            monitor_job()
            
            # 等待指定的时间间隔
            logger.info(f"等待 {interval} 秒后进行下一次检查...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")

if __name__ == "__main__":
    # 启动简单定时循环，每60秒执行一次
    start_simple_scheduler(60) 