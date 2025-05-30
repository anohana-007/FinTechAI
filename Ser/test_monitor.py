"""
测试股票价格监控功能
"""
import json
from services.monitor_service import check_thresholds, format_alert_message

def test_check_thresholds():
    """测试检查阈值功能"""
    print("开始测试股票阈值检查功能...")
    
    # 执行检查
    alerts = check_thresholds()
    
    # 显示结果
    if alerts:
        print(f"检测到 {len(alerts)} 个股票价格预警:")
        for i, alert in enumerate(alerts, 1):
            print(f"\n预警 #{i}:")
            print(format_alert_message(alert))
            print("-" * 50)
    else:
        print("没有检测到股票价格预警")

def print_watchlist():
    """打印当前关注列表"""
    try:
        with open('data/watchlist.json', 'r', encoding='utf-8') as f:
            watchlist = json.load(f)
            
        print(f"\n当前关注列表: {len(watchlist)} 只股票")
        for i, stock in enumerate(watchlist, 1):
            print(f"{i}. {stock['stock_name']} ({stock['stock_code']})")
            print(f"   上限: {stock['upper_threshold']}, 下限: {stock['lower_threshold']}")
            print(f"   邮箱: {stock['user_email']}")
            print(f"   添加时间: {stock.get('added_at', '未知')}")
            print()
    except Exception as e:
        print(f"读取关注列表出错: {e}")

if __name__ == "__main__":
    # 打印当前关注列表
    print_watchlist()
    
    # 测试阈值检查
    test_check_thresholds() 