import time
import tushare as ts
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import akshare as ak

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
    
    if not token:
        print(f"警告: 未设置TUSHARE_TOKEN。用户配置token: {'有' if user_config and user_config.get('tushare_token') else '无'}")
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
    pd.DataFrame: 包含股票代码和名称的DataFrame，失败时返回None
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
            print("Tushare初始化失败，无法获取股票列表")
            return None
        
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
            print("未获取到任何股票数据")
            return None
            
    except Exception as e:
        print(f"获取股票列表时出错: {e}")
        return None

def search_stocks(query, limit=20, user_config: Optional[Dict[str, Any]] = None):
    """
    [已弃用 - 使用 search_stocks_akshare] 搜索股票 (基于Tushare get_all_stocks)
    """
    print("警告: 调用了已弃用的 search_stocks (Tushare) 函数。请迁移到AKShare版本。")
    return []
    # try:
    #     # 获取股票列表
    #     stocks_df = get_all_stocks(user_config)
        
    #     if stocks_df is None or stocks_df.empty:
    #         return []
        
    #     # 搜索逻辑
    #     query = query.strip().upper()
    #     results = []
        
    #     # 如果查询为空，返回空结果
    #     if not query:
    #         return []
        
    #     # 遍历股票列表进行匹配
    #     for _, row in stocks_df.iterrows():
    #         code = row['ts_code']
    #         name = row['name']
            
    #         # 匹配股票代码（去掉后缀）
    #         code_without_suffix = code.split('.')[0]
    #         if query in code_without_suffix:
    #             results.append({
    #                 'code': code,
    #                 'name': name,
    #                 'match_type': 'code'
    #             })
    #             continue
            
    #         # 匹配股票名称
    #         if query in name:
    #             results.append({
    #                 'code': code,
    #                 'name': name,
    #                 'match_type': 'name'
    #             })
        
    #     # 按匹配类型排序：代码匹配优先，然后是名称匹配
    #     results.sort(key=lambda x: (x['match_type'] == 'name', x['name']))
        
    #     # 限制返回数量
    #     return results[:limit]
        
    # except Exception as e:
    #     print(f"搜索股票时出错: {e}")
    #     return []

# 新增：基于AKShare的股票搜索函数
def search_stocks_akshare(keyword: str, limit: int = 20) -> Dict[str, Any]:
    """
    使用 AKShare 搜索股票。
    返回格式: {'success': bool, 'data': list, 'message': str, 'error': str | None}
    data 列表内元素格式: {'stock_code': str, 'stock_name': str, 'match_type': str}
    """
    results = []
    keyword = keyword.strip()
    if not keyword:
        return {'success': True, 'data': [], 'message': '关键词为空', 'error': None}

    try:
        print(f"AKShare 正在搜索: {keyword}")
        
        # 使用 ak.stock_info_a_code_name 获取A股股票基本信息
        # 这个函数返回包含所有A股代码和名称的DataFrame
        stock_df = ak.stock_info_a_code_name()
        
        if stock_df.empty:
            return {'success': True, 'data': [], 'message': f"AKShare返回空数据", 'error': None}

        print(f"AKShare 获取到 {len(stock_df)} 只股票数据，开始搜索匹配")
        
        # 确保DataFrame有我们需要的列
        # stock_info_a_code_name 通常返回的列包括: code, name, 等
        if 'code' not in stock_df.columns or 'name' not in stock_df.columns:
            # 尝试其他可能的列名
            available_columns = stock_df.columns.tolist()
            print(f"AKShare 返回的列名: {available_columns}")
            
            # 常见的列名映射
            code_col = None
            name_col = None
            
            for col in available_columns:
                if col.lower() in ['code', 'stock_code', 'symbol', '股票代码', '代码']:
                    code_col = col
                elif col.lower() in ['name', 'stock_name', '股票名称', '名称', '简称']:
                    name_col = col
            
            if not code_col or not name_col:
                return {'success': False, 'data': [], 'message': f'AKShare数据格式不符合预期，可用列: {available_columns}', 'error': 'AKSHARE_DATA_FORMAT_ERROR'}
        else:
            code_col = 'code'
            name_col = 'name'

        matched_count = 0
        keyword_upper = keyword.upper()
        
        # 在股票数据中搜索匹配项
        for _, row in stock_df.iterrows():
            stock_code = str(row[code_col]).strip()
            stock_name = str(row[name_col]).strip()
            
            # 跳过无效数据
            if not stock_code or not stock_name or stock_code == 'nan' or stock_name == 'nan':
                continue
            
            match_type = 'unknown'
            is_match = False
            
            # 判断匹配类型和是否匹配
            if keyword_upper in stock_code.upper():
                match_type = 'code'
                is_match = True
            elif keyword_upper in stock_name.upper():
                match_type = 'name' 
                is_match = True
            
            if is_match:
                # 格式化股票代码为标准格式 (例如: 600000.SH, 000001.SZ)
                formatted_code = stock_code
                if '.' not in stock_code:
                    # 如果代码没有后缀，根据代码规则添加
                    if stock_code.startswith('6'):
                        formatted_code = f"{stock_code}.SH"  # 上海股票
                    elif stock_code.startswith('0') or stock_code.startswith('3'):
                        formatted_code = f"{stock_code}.SZ"  # 深圳股票
                    elif stock_code.startswith('8') or stock_code.startswith('4'):
                        formatted_code = f"{stock_code}.BJ"  # 北交所（如果支持）
                
                results.append({
                    'stock_code': formatted_code,
                    'stock_name': stock_name,
                    'match_type': match_type
                })
                matched_count += 1
                
                if matched_count >= limit:
                    break
        
        # 排序：代码匹配优先，然后是名称，再按代码排序
        results.sort(key=lambda x: (x['match_type'] != 'code', x['match_type'] != 'name', x['stock_code']))

        print(f"AKShare 搜索到 {len(results)} 条结果 for '{keyword}'")
        return {'success': True, 'data': results, 'message': f"成功获取 {len(results)} 条结果", 'error': None}

    except Exception as e:
        error_msg = str(e)
        print(f"AKShare 搜索股票时出错: {error_msg}")
        
        # 根据错误类型提供更具体的错误信息
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            return {'success': False, 'data': [], 'message': 'AKShare请求超时，请稍后重试', 'error': 'AKSHARE_TIMEOUT'}
        elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
            return {'success': False, 'data': [], 'message': 'AKShare网络连接失败，请检查网络', 'error': 'AKSHARE_NETWORK_ERROR'}
        elif 'no attribute' in error_msg.lower():
            return {'success': False, 'data': [], 'message': f'AKShare函数不存在: {error_msg}', 'error': 'AKSHARE_FUNCTION_NOT_FOUND'}
        else:
            return {'success': False, 'data': [], 'message': f'AKShare搜索失败: {error_msg}', 'error': 'AKSHARE_SEARCH_ERROR'}

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
            print("⚠️ Tushare Token无效，无法获取股票价格")
            return None
        
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
                print(f"❌ 无法获取股票 {stock_code} 的历史数据")
                return None
            
        # 返回收盘价
        real_price = float(df.iloc[0]['close'])
        print(f"✅ 获取真实股价: {stock_code} = ¥{real_price}")
        return real_price
    
    except Exception as e:
        print(f"获取股票价格时出错: {e}")
        return None

def validate_tushare_token(token: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    验证Tushare Token的有效性
    
    参数:
    token (str): Tushare API Token
    user_config (dict, optional): 用户配置
    
    返回:
    dict: 验证结果 {'valid': bool, 'message': str, 'details': dict}
    """
    if not token or not token.strip():
        return {
            'valid': False,
            'message': 'Token不能为空',
            'details': {}
        }
    
    try:
        # 设置token
        ts.set_token(token.strip())
        
        # 创建API接口
        pro = ts.pro_api()
        
        # 尝试调用一个简单的API来验证token
        # 使用stock_basic API，获取少量数据
        print("🔍 正在验证Tushare Token...")
        df = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name')
        
        if df is not None and not df.empty:
            print(f"✅ Tushare Token验证成功，获取到 {len(df)} 条股票数据")
            return {
                'valid': True,
                'message': 'Token验证成功',
                'details': {
                    'test_api': 'stock_basic',
                    'sample_count': len(df),
                    'sample_stocks': df.head(3).to_dict('records') if len(df) > 0 else []
                }
            }
        else:
            print("⚠️ Tushare Token有效但API返回空数据")
            return {
                'valid': False,
                'message': 'Token有效但API返回空数据',
                'details': {'test_api': 'stock_basic'}
            }
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ Tushare Token验证失败: {error_message}")
        
        # 根据错误信息提供更具体的建议
        if '请求过于频繁' in error_message:
            suggestion = '请求过于频繁，请稍后重试'
        elif 'token' in error_message.lower() or '您的token不对' in error_message:
            suggestion = 'Token格式错误或已失效，请检查Token是否正确'
        elif '权限不足' in error_message:
            suggestion = '账户权限不足，请检查Tushare账户状态'
        elif '积分不足' in error_message:
            suggestion = '账户积分不足，请充值或升级账户'
        elif 'timeout' in error_message.lower() or 'connection' in error_message.lower():
            suggestion = '网络连接超时，请检查网络连接或代理设置'
        else:
            suggestion = '网络错误或服务暂时不可用，请稍后重试'
        
        return {
            'valid': False,
            'message': f'Token验证失败: {suggestion}',
            'details': {
                'error': error_message,
                'suggestion': suggestion
            }
        }

# 修改 search_stocks_by_keyword 以使用 AKShare
def search_stocks_by_keyword(user_tushare_token: str, keyword: str, limit: int = 20) -> Dict[str, Any]:
    """
    根据关键词搜索股票，专门用于API端点。现在使用AKShare进行搜索。
    Tushare Token 仍作为参数传入，因为此函数签名被API层使用，且Tushare初始化可能仍需检查。
    但核心搜索逻辑已改为AKShare。
    """
    try:
        # 验证参数 (keyword)
        if not keyword or not keyword.strip():
            return {
                'success': False,
                'data': [],
                'message': '搜索关键词不能为空',
                'error': 'KEYWORD_EMPTY'
            }

        # Tushare Token 验证逻辑 (主要为股价获取等其他依赖Tushare的功能服务)
        # 对于纯AKShare搜索，此处的Token缺失不应直接阻止搜索，但API层可能仍有检查。
        # 如果API层仍检查Token，这里的逻辑需要调整。
        # 假设API层仍会进行Tushare Token检查，所以我们保留user_config的创建和init_tushare。
        if not user_tushare_token or not user_tushare_token.strip():
            # 如果搜索本身不依赖Tushare Token, 这个错误可以调整
            # 但如果其他操作如股价获取需要，这个检查仍然重要
             return {
                'success': False,
                'data': [],
                'message': '用户未配置Tushare Token (用于获取股价等功能)',
                'error': 'TUSHARE_TOKEN_MISSING_FOR_OTHER_FEATURES' # 新的错误码
            }
        
        user_config = {'tushare_token': user_tushare_token.strip()}
        if not init_tushare(user_config): # 初始化Tushare主要为后续获取价格等服务
            print("警告: Tushare初始化失败。搜索将继续使用AKShare，但获取股价等功能可能受影响。")
            # 即使Tushare初始化失败，也允许AKShare搜索继续
            # 但需要前端能处理后续获取股价失败的情况
            # 或者，如果API严格要求Tushare Token有效，这里应该返回错误
            # return {
            #     'success': False,
            #     'data': [],
            #     'message': 'Tushare Token无效或网络连接失败 (影响股价获取)',
            #     'error': 'TUSHARE_TOKEN_INVALID_FOR_OTHER_FEATURES' # 新的错误码
            # }

        # 执行 AKShare 搜索
        akshare_search_result = search_stocks_akshare(keyword.strip(), limit)
        
        if not akshare_search_result['success']:
            return {
                'success': False,
                'data': [],
                'message': akshare_search_result['message'],
                'error': akshare_search_result.get('error', 'AKSHARE_SEARCH_FAILED')
            }
        
        results = akshare_search_result['data']
        
        if not results:
            return {
                'success': True,
                'data': [],
                'message': f"未找到匹配 '{keyword}' 的股票 (来自AKShare)",
                'error': None
            }
        
        # 结果已由 search_stocks_akshare 格式化
        return {
            'success': True,
            'data': results,
            'message': f"找到 {len(results)} 个匹配结果 (来自AKShare)",
            'error': None
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"search_stocks_by_keyword 执行时出错: {error_message}")
        # 通用错误处理
        return {
            'success': False,
            'data': [],
            'message': f'搜索失败: {error_message}',
            'error': 'UNKNOWN_SEARCH_ERROR'
        } 