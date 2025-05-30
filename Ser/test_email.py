"""
测试邮件发送功能
"""
import os
from services.email_service import send_email_alert, format_stock_alert_email

def test_email_config():
    """测试邮件配置是否正确"""
    print("检查邮件配置...")
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    print(f"SMTP服务器: {smtp_server or '未设置'}")
    print(f"SMTP端口: {smtp_port or '未设置'}")
    print(f"SMTP用户名: {smtp_username[:4] + '***' if smtp_username and len(smtp_username) > 4 else '未设置'}")
    print(f"SMTP密码: {'已设置' if smtp_password else '未设置'}")
    
    if not smtp_server or not smtp_port or not smtp_username or not smtp_password:
        print("\n警告: 邮件配置不完整，请检查.env文件")
        print("请参考env.example文件设置正确的邮件配置")
        return False
    
    print("\n邮件配置看起来正确")
    return True

def test_send_email():
    """测试发送邮件"""
    if not test_email_config():
        return
    
    print("\n测试发送邮件...")
    test_email = input("请输入测试邮箱地址: ").strip()
    
    if not test_email:
        print("邮箱地址为空，测试取消")
        return
    
    # 创建测试邮件内容
    subject = "股票盯盘系统邮件测试"
    body = """
这是一封来自股票盯盘系统的测试邮件。

如果您收到这封邮件，说明邮件发送功能配置正确。

--------------------------------
此邮件由股票盯盘系统自动发送，请勿回复。
"""
    
    # 发送测试邮件
    success = send_email_alert(test_email, subject, body)
    
    if success:
        print(f"\n测试邮件已发送至 {test_email}，请检查您的邮箱")
    else:
        print("\n邮件发送失败，请检查日志获取详细错误信息")

def test_alert_email():
    """测试警报邮件格式"""
    print("\n测试警报邮件格式...")
    
    # 模拟警报数据
    alert = {
        'stock_code': '600036.SH',
        'stock_name': '招商银行',
        'current_price': 45.75,
        'threshold': 45.50,
        'direction': 'UP',
        'user_email': 'test@example.com',
        'timestamp': '2023-05-30 14:30:00'
    }
    
    # 格式化邮件内容
    subject, body = format_stock_alert_email(alert)
    
    print(f"邮件主题: {subject}")
    print("\n邮件内容:")
    print(body)
    
    # 是否发送测试警报邮件
    send_test = input("\n是否发送测试警报邮件? (y/n): ").strip().lower()
    
    if send_test == 'y':
        test_email = input("请输入测试邮箱地址: ").strip()
        
        if test_email:
            success = send_email_alert(test_email, subject, body)
            
            if success:
                print(f"\n测试警报邮件已发送至 {test_email}，请检查您的邮箱")
            else:
                print("\n邮件发送失败，请检查日志获取详细错误信息")

if __name__ == "__main__":
    # 测试邮件配置
    test_email_config()
    
    # 测试警报邮件格式
    test_alert_email()
    
    # 测试发送普通邮件
    # test_send_email() 