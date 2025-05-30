import json
import os
import re
from datetime import datetime

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
WATCHLIST_FILE = os.path.join(DATA_DIR, 'watchlist.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

def get_watchlist():
    """
    获取用户关注的股票列表
    
    返回:
    list: 股票列表
    """
    try:
        if not os.path.exists(WATCHLIST_FILE):
            return []
            
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取关注列表出错: {e}")
        return []

def save_watchlist(watchlist):
    """
    保存用户关注的股票列表
    
    参数:
    watchlist (list): 股票列表
    
    返回:
    bool: 保存是否成功
    """
    try:
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存关注列表出错: {e}")
        return False

def add_stock(stock_data):
    """
    添加股票到关注列表
    
    参数:
    stock_data (dict): 股票信息，包含以下字段:
        - stock_code: 股票代码
        - stock_name: 股票名称
        - upper_threshold: 上限阈值
        - lower_threshold: 下限阈值
        - user_email: 用户邮箱
    
    返回:
    tuple: (成功标志, 消息)
    """
    # 验证输入
    if not validate_stock_data(stock_data):
        return False, "输入数据格式不正确"
    
    # 读取现有列表
    watchlist = get_watchlist()
    
    # 检查股票是否已存在
    for stock in watchlist:
        if stock['stock_code'] == stock_data['stock_code'] and stock['user_email'] == stock_data['user_email']:
            return False, "该股票已在关注列表中"
    
    # 添加时间戳
    stock_data['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 添加到列表
    watchlist.append(stock_data)
    
    # 保存
    if save_watchlist(watchlist):
        return True, "股票添加成功"
    else:
        return False, "保存失败，请稍后重试"

def validate_stock_data(data):
    """
    验证股票数据是否有效
    
    参数:
    data (dict): 股票数据
    
    返回:
    bool: 数据是否有效
    """
    # 检查必要字段
    required_fields = ['stock_code', 'stock_name', 'upper_threshold', 'lower_threshold', 'user_email']
    if not all(field in data for field in required_fields):
        return False
    
    # 验证股票代码格式 (简单验证，可根据实际需求调整)
    if not re.match(r'^\d{6}\.[A-Z]{2}$', data['stock_code']):
        return False
    
    # 验证阈值是数字
    try:
        float(data['upper_threshold'])
        float(data['lower_threshold'])
    except (ValueError, TypeError):
        return False
    
    # 验证下限小于上限
    if float(data['lower_threshold']) >= float(data['upper_threshold']):
        return False
    
    # 验证邮箱格式
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['user_email']):
        return False
    
    return True 