import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional, Dict, Any
from .ai_analysis_service import get_basic_ai_analysis

# 默认邮件配置（作为后备配置）
DEFAULT_SMTP_SERVER = 'smtp.163.com'
DEFAULT_SMTP_PORT = 25
DEFAULT_SMTP_USE_SSL = False

# 日志配置
logger = logging.getLogger('email_service')

def send_email_alert(recipient_email, subject, body, user_config: Optional[Dict[str, Any]] = None):
    """
    发送邮件提醒
    
    参数:
    recipient_email (str): 收件人邮箱
    subject (str): 邮件主题
    body (str): 邮件内容
    user_config (dict, optional): 用户配置，包含邮件设置
    
    返回:
    bool: 发送是否成功
    """
    # 优先使用用户配置，否则使用全局配置
    if user_config:
        smtp_server = user_config.get('email_smtp_server', DEFAULT_SMTP_SERVER)
        smtp_port = user_config.get('email_smtp_port', DEFAULT_SMTP_PORT)
        smtp_user = user_config.get('email_smtp_user', '')
        smtp_password = user_config.get('email_smtp_password', '')
        email_sender = user_config.get('email_sender_address', smtp_user)
    else:
        smtp_server = DEFAULT_SMTP_SERVER
        smtp_port = DEFAULT_SMTP_PORT
        smtp_user = ''
        smtp_password = ''
        email_sender = smtp_user
    
    if not smtp_user or not smtp_password:
        logger.error("未配置邮箱账号密码，无法发送邮件。请配置邮件设置")
        return False
        
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = f"{Header('股票价格提醒', 'utf-8').encode()} <{email_sender}>"
        msg['To'] = recipient_email
        msg['Subject'] = Header(subject, 'utf-8').encode()
        
        # 添加邮件内容
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器
        # 判断是否使用SSL（基于端口号自动判断或者用户配置）
        use_ssl = smtp_port == 465 or DEFAULT_SMTP_USE_SSL
        
        if use_ssl:
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.ehlo()
            # 部分服务器需要启用STARTTLS
            if smtp.has_extn('STARTTLS'):
                smtp.starttls()
                smtp.ehlo()
        
        # 登录
        smtp.login(smtp_user, smtp_password)
        
        # 发送邮件
        smtp.sendmail(email_sender, recipient_email, msg.as_string())
        
        # 关闭连接
        smtp.quit()
        
        logger.info(f"成功发送邮件提醒至 {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False

def format_stock_alert_email(alert, ai_analysis=None, user_config: Optional[Dict[str, Any]] = None):
    """
    格式化股票价格提醒邮件内容
    
    参数:
    alert (dict): 警报信息，包含股票代码、名称、价格等信息
    ai_analysis (str, optional): AI分析结果
    user_config (dict, optional): 用户配置，用于获取AI API密钥
    
    返回:
    tuple: (邮件主题, 邮件内容)
    """
    direction = "上涨" if alert['direction'] == 'UP' else "下跌"
    direction_symbol = "[UP]" if alert['direction'] == 'UP' else "[DOWN]"
    
    subject = f"{direction_symbol} 股票价格提醒: {alert['stock_name']}已{direction}至阈值价格"
    
    # 如果没有提供AI分析结果且启用了AI分析，则获取分析
    if ai_analysis is None:
        try:
            ai_analysis = get_basic_ai_analysis(
                alert['stock_code'], 
                alert['current_price'], 
                alert['direction'],
                user_config
            )
        except Exception as e:
            logger.error(f"获取AI分析时出错: {e}")
            ai_analysis = "AI分析暂不可用"
    
    # 构建邮件正文
    body = f"""尊敬的用户：

您关注的股票 {alert['stock_name']}({alert['stock_code']}) 价格已发生重要变动。

当前价格: {alert['current_price']} 
阈值价格: {alert['threshold']}
变动方向: {direction} {direction_symbol}
提醒时间: {alert['timestamp']}
"""

    # 添加AI分析部分
    if ai_analysis:
        body += f"""
---------- AI分析 ----------
{ai_analysis}
----------------------------
"""

    body += """
请及时查看您的股票交易账户，并根据市场情况做出相应决策。

--------------------------------
此邮件由股票盯盘系统自动发送，请勿回复。
"""
    
    return subject, body 