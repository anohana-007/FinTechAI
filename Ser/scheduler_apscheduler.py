"""
使用APScheduler库实现的定时监控服务
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.monitor_service import check_thresholds, format_alert_message

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scheduler")

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

def start_scheduler():
    """启动定时任务调度器"""
    logger.info("启动APScheduler定时任务调度器...")
    
    # 创建调度器
    scheduler = BackgroundScheduler()
    
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
    logger.info("调度器已启动，按Ctrl+C停止")
    
    try:
        # 保持主线程运行
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        # 关闭调度器
        scheduler.shutdown()
        logger.info("调度器已关闭")

if __name__ == "__main__":
    start_scheduler() 