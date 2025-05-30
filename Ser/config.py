import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# Tushare API配置
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')

# 邮件配置
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.163.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '25'))
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_SENDER = os.getenv('EMAIL_SENDER', SMTP_USERNAME)
ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true'

# 应用配置
DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
PORT = int(os.getenv('FLASK_PORT', '5000')) 