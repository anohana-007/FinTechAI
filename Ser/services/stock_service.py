import os
import time
import tushare as ts
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# 加载.env文件
load_dotenv()

# Tushare API Token配置
# 注意：需要注册tushare账号并获取token
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')

# 全局变量用于缓存股票列表
_cached_stock_list = None
_cache_timestamp = None
CACHE_EXPIRY_HOURS = 24  # 缓存24小时

# 初始化tushare
def init_tushare(user_config: Optional[Dict[str, Any]] = None):
    """
    初始化tushare API
    
    参数:
    user_config (dict, optional): 用户配置，包含tushare_token
    
    返回:
    bool: 初始化是否成功
    """
    # 优先使用用户配置的token，否则使用全局配置
    token = None
    if user_config and user_config.get('tushare_token'):
        token = user_config['tushare_token']
    else:
        token = TUSHARE_TOKEN
    
    if not token:
        print(f"警告: 未设置TUSHARE_TOKEN。用户配置token: {'有' if user_config and user_config.get('tushare_token') else '无'}")
        print(f"全局token: {'有' if TUSHARE_TOKEN else '无'}")
        return False
    
    print(f"使用Tushare Token: {token[:4]}***")
    try:
        ts.set_token(token)
        return True
    except Exception as e:
        print(f"Tushare初始化失败: {e}")
        return False

def get_all_stocks(user_config: Optional[Dict[str, Any]] = None):
    """
    获取所有A股股票列表
    
    参数:
    user_config (dict, optional): 用户配置
    
    返回:
    pd.DataFrame: 包含股票代码和名称的DataFrame
    """
    global _cached_stock_list, _cache_timestamp
    
    # 检查缓存是否有效
    if (_cached_stock_list is not None and 
        _cache_timestamp is not None and 
        datetime.now().timestamp() - _cache_timestamp < CACHE_EXPIRY_HOURS * 3600):
        return _cached_stock_list
    
    try:
        # 初始化tushare
        if not init_tushare(user_config):
            # 如果初始化失败，返回模拟数据
            return _get_mock_stock_list()
        
        # 创建tushare pro API接口
        pro = ts.pro_api()
        
        # 获取股票基本信息
        # exchange: 'SSE'上交所 'SZSE'深交所
        stock_list = []
        
        # 获取上交所股票
        df_sse = pro.stock_basic(exchange='SSE', list_status='L')
        if not df_sse.empty:
            stock_list.append(df_sse[['ts_code', 'name']])
        
        # 获取深交所股票
        df_szse = pro.stock_basic(exchange='SZSE', list_status='L')
        if not df_szse.empty:
            stock_list.append(df_szse[['ts_code', 'name']])
        
        # 合并数据
        if stock_list:
            all_stocks = pd.concat(stock_list, ignore_index=True)
            
            # 缓存结果
            _cached_stock_list = all_stocks
            _cache_timestamp = datetime.now().timestamp()
            
            return all_stocks
        else:
            return _get_mock_stock_list()
            
    except Exception as e:
        print(f"获取股票列表时出错: {e}")
        return _get_mock_stock_list()

def _get_mock_stock_list():
    """
    获取模拟股票列表（用于开发测试）
    
    返回:
    pd.DataFrame: 模拟股票数据
    """
    mock_data = {
        'ts_code': [
            '600036.SH', '000001.SZ', '000002.SZ', '600000.SH', '600519.SH',
            '000858.SZ', '002415.SZ', '600276.SH', '002594.SZ', '000166.SZ',
            '600887.SH', '002230.SZ', '000568.SZ', '600031.SH', '002142.SZ',
            '000063.SZ', '002304.SZ', '600837.SH', '000876.SZ', '600104.SH'
        ],
        'name': [
            '招商银行', '平安银行', '万科A', '浦发银行', '贵州茅台',
            '五粮液', '海康威视', '恒瑞医药', '比亚迪', '申万宏源',
            '伊利股份', '科大讯飞', '泸州老窖', '三一重工', '宁波银行',
            '中兴通讯', '洋河股份', '海通证券', '新希望', '上汽集团'
        ]
    }
    
    return pd.DataFrame(mock_data)

def search_stocks(query, limit=20, user_config: Optional[Dict[str, Any]] = None):
    """
    搜索股票
    
    参数:
    query (str): 搜索关键词（股票名称或代码）
    limit (int): 返回结果数量限制
    user_config (dict, optional): 用户配置
    
    返回:
    list: 匹配的股票列表 [{'code': '600036.SH', 'name': '招商银行'}, ...]
    """
    try:
        # 获取股票列表
        stocks_df = get_all_stocks(user_config)
        
        if stocks_df is None or stocks_df.empty:
            return []
        
        # 搜索逻辑
        query = query.strip().upper()
        results = []
        
        # 如果查询为空，返回空结果
        if not query:
            return []
        
        # 遍历股票列表进行匹配
        for _, row in stocks_df.iterrows():
            code = row['ts_code']
            name = row['name']
            
            # 匹配股票代码（去掉后缀）
            code_without_suffix = code.split('.')[0]
            if query in code_without_suffix:
                results.append({
                    'code': code,
                    'name': name,
                    'match_type': 'code'
                })
                continue
            
            # 匹配股票名称
            if query in name:
                results.append({
                    'code': code,
                    'name': name,
                    'match_type': 'name'
                })
        
        # 按匹配类型排序：代码匹配优先，然后是名称匹配
        results.sort(key=lambda x: (x['match_type'] == 'name', x['name']))
        
        # 限制返回数量
        return results[:limit]
        
    except Exception as e:
        print(f"搜索股票时出错: {e}")
        return []

# 获取股票最新价格
def get_stock_price(stock_code, user_config: Optional[Dict[str, Any]] = None):
    """
    获取指定股票代码的最新价格
    
    参数:
    stock_code (str): 股票代码，例如'600036.SH'
    user_config (dict, optional): 用户配置，包含tushare_token
    
    返回:
    float: 股票当前价格，如获取失败则返回None
    """
    try:
        # 初始化tushare
        if not init_tushare(user_config):
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