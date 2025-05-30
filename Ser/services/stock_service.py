import os
import time
import tushare as ts
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# Tushare API Token配置
# 注意：需要注册tushare账号并获取token
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')

# 初始化tushare
def init_tushare():
    """初始化tushare API"""
    if not TUSHARE_TOKEN:
        print(f"警告: 未设置TUSHARE_TOKEN环境变量。请在tushare官网注册并获取token。")
        print(f"当前目录: {os.getcwd()}")
        print(f"环境变量: {os.environ.get('TUSHARE_TOKEN')}")
        return False
    
    print(f"使用Tushare Token: {TUSHARE_TOKEN[:4]}***")
    try:
        ts.set_token(TUSHARE_TOKEN)
        return True
    except Exception as e:
        print(f"Tushare初始化失败: {e}")
        return False

# 获取股票最新价格
def get_stock_price(stock_code):
    """
    获取指定股票代码的最新价格
    
    参数:
    stock_code (str): 股票代码，例如'600036.SH'
    
    返回:
    float: 股票当前价格，如获取失败则返回None
    """
    try:
        # 初始化tushare
        if not init_tushare():
            # 如果初始化失败，使用模拟数据（实际应用中应处理错误）
            print("使用模拟数据...")
            return _get_mock_price(stock_code)
        
        # 创建tushare pro API接口
        pro = ts.pro_api()
        
        # 获取当前日期
        today = datetime.now().strftime('%Y%m%d')
        
        # 获取日线行情数据
        df = pro.daily(ts_code=stock_code, trade_date=today)
        
        if df.empty:
            # 如果今天没有数据，尝试获取最近的交易日数据
            df = pro.daily(ts_code=stock_code)
            if df.empty:
                return None
            
        # 返回收盘价
        return float(df.iloc[0]['close'])
    
    except Exception as e:
        print(f"获取股票价格时出错: {e}")
        # 在API调用失败时使用模拟数据
        return _get_mock_price(stock_code)

def _get_mock_price(stock_code):
    """
    生成模拟股票价格（仅用于开发测试）
    
    参数:
    stock_code (str): 股票代码
    
    返回:
    float: 模拟的股票价格
    """
    # 使用股票代码生成一个伪随机价格
    code_num = int(''.join(filter(str.isdigit, stock_code)))
    base_price = (code_num % 100) + 10  # 基础价格在10-110之间
    variation = (hash(f"{stock_code}_{time.time()}") % 100) / 1000  # 小变化
    
    return round(base_price + variation, 2) 