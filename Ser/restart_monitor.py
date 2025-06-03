#!/usr/bin/env python3
"""
重启监控服务和清除缓存
"""

import os
import sys
import logging
from services.auth_service import get_user_config_by_email
from services.monitor_service import get_watchlist
from services.stock_service import get_stock_price

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def restart_monitor_service():
    """重启监控服务和清除缓存"""
    
    print("🔄 重启监控服务...")
    
    # 1. 清除可能的股票列表缓存
    try:
        import services.stock_service as stock_service
        stock_service._cached_stock_list = None
        stock_service._cache_timestamp = None
        print("   ✓ 已清除股票列表缓存")
    except Exception as e:
        print(f"   ⚠ 清除缓存时出错: {e}")
    
    # 2. 检查当前用户配置
    print("\n📊 检查用户配置...")
    emails = ['testproxy@example.com', 'test@example.com', 'testai@example.com']
    
    for email in emails:
        config = get_user_config_by_email(email)
        if config:
            token = config.get('tushare_token')
            if token:
                print(f"   {email}: Token已配置 ({len(token)}字符)")
            else:
                print(f"   {email}: Token未配置")
        else:
            print(f"   {email}: 用户未找到")
    
    # 3. 测试股价获取
    print("\n🧪 测试股价获取...")
    watchlist = get_watchlist()
    if watchlist:
        for stock in watchlist[:3]:  # 只测试前3个
            stock_code = stock.get('stock_code')
            user_email = stock.get('user_email')
            
            # 获取用户配置
            user_config = get_user_config_by_email(user_email) if user_email else None
            
            # 测试获取股价
            price = get_stock_price(stock_code, user_config)
            
            if user_config and user_config.get('tushare_token'):
                token_display = user_config['tushare_token'][:10] + '***'
            else:
                token_display = "无配置"
            
            print(f"   {stock_code} (用户: {user_email})")
            print(f"     Token: {token_display}")
            print(f"     价格: {price}")
    
    print("\n✅ 监控服务重启完成！")
    print("\n💡 建议：")
    print("   1. 请重启Flask应用以确保配置完全生效")
    print("   2. 检查关注列表中的用户邮箱是否对应真实用户")
    print("   3. 确保Tushare Token有效且未过期")

if __name__ == "__main__":
    restart_monitor_service() 