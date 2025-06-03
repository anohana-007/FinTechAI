import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

# 配置日志
logger = logging.getLogger('database_service')

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stock_monitor.db')

def init_database():
    """
    初始化数据库，创建必要的表
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                tushare_token TEXT,
                email_sender_address TEXT,
                email_smtp_server TEXT,
                email_smtp_port INTEGER DEFAULT 587,
                email_smtp_user TEXT,
                email_smtp_password_encrypted TEXT,
                ai_api_keys_json_encrypted TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建告警日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                alert_timestamp DATETIME NOT NULL,
                triggered_price REAL NOT NULL,
                threshold_price REAL NOT NULL,
                direction TEXT NOT NULL CHECK (direction IN ('UP', 'DOWN')),
                ai_analysis TEXT,
                user_email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email)
        ''')
        
        # 创建告警日志表索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alert_logs_stock_code 
            ON alert_logs(stock_code)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alert_logs_timestamp 
            ON alert_logs(alert_timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alert_logs_user_email 
            ON alert_logs(user_email)
        ''')
        
        # 提交更改
        conn.commit()
        
        logger.info("数据库初始化成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def save_alert_log(alert_data: Dict) -> int:
    """
    保存告警日志到数据库
    
    参数:
    alert_data (dict): 告警数据，包含以下字段:
        - stock_code: 股票代码
        - stock_name: 股票名称
        - triggered_price: 触发价格
        - threshold_price: 阈值价格
        - direction: 方向 ('UP' 或 'DOWN')
        - ai_analysis: AI分析结果 (可选)
        - user_email: 用户邮箱
        - alert_timestamp: 告警时间 (可选，默认当前时间)
    
    返回:
    int: 插入记录的ID
    """
    try:
        # 确保数据库已初始化
        init_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 准备数据
        stock_code = alert_data['stock_code']
        stock_name = alert_data['stock_name']
        triggered_price = float(alert_data['triggered_price'])
        threshold_price = float(alert_data.get('threshold_price', alert_data.get('threshold', 0)))
        direction = alert_data['direction']
        ai_analysis = alert_data.get('ai_analysis', '')
        user_email = alert_data.get('user_email', '')
        
        # 处理时间戳
        if 'alert_timestamp' in alert_data:
            if isinstance(alert_data['alert_timestamp'], str):
                alert_timestamp = datetime.fromisoformat(alert_data['alert_timestamp'].replace('Z', '+00:00'))
            else:
                alert_timestamp = alert_data['alert_timestamp']
        else:
            alert_timestamp = datetime.now()
        
        # 插入数据
        cursor.execute('''
            INSERT INTO alert_logs 
            (stock_code, stock_name, alert_timestamp, triggered_price, threshold_price, 
             direction, ai_analysis, user_email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (stock_code, stock_name, alert_timestamp, triggered_price, threshold_price,
              direction, ai_analysis, user_email))
        
        # 获取插入记录的ID
        alert_id = cursor.lastrowid
        
        # 提交更改
        conn.commit()
        
        logger.info(f"告警日志保存成功: ID={alert_id}, {stock_code} {direction} {triggered_price}")
        
        return alert_id
        
    except Exception as e:
        logger.error(f"保存告警日志失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_alert_logs(
    user_email: Optional[str] = None,
    stock_code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]:
    """
    查询告警日志
    
    参数:
    user_email (str, optional): 用户邮箱过滤
    stock_code (str, optional): 股票代码过滤
    start_date (datetime, optional): 开始时间
    end_date (datetime, optional): 结束时间
    limit (int): 返回记录数量限制
    offset (int): 偏移量（用于分页）
    
    返回:
    List[Dict]: 告警日志列表
    """
    try:
        # 确保数据库已初始化
        init_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
        cursor = conn.cursor()
        
        # 构建查询语句
        query = '''
            SELECT id, user_id, stock_code, stock_name, alert_timestamp, 
                   triggered_price, threshold_price, direction, ai_analysis, 
                   user_email, created_at, updated_at
            FROM alert_logs
            WHERE 1=1
        '''
        params = []
        
        # 添加过滤条件
        if user_email:
            query += ' AND user_email = ?'
            params.append(user_email)
        
        if stock_code:
            query += ' AND stock_code = ?'
            params.append(stock_code)
        
        if start_date:
            query += ' AND alert_timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND alert_timestamp <= ?'
            params.append(end_date)
        
        # 排序和分页
        query += ' ORDER BY alert_timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # 执行查询
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 转换为字典列表
        results = []
        for row in rows:
            # 处理AI分析数据，尝试解析JSON格式
            ai_analysis = row['ai_analysis']
            if ai_analysis:
                try:
                    # 尝试解析JSON格式的AI分析
                    ai_analysis = json.loads(ai_analysis)
                except (json.JSONDecodeError, TypeError):
                    # 如果不是JSON格式，保持原文本
                    pass
            
            results.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'stock_code': row['stock_code'],
                'stock_name': row['stock_name'],
                'alert_timestamp': row['alert_timestamp'],
                'triggered_price': row['triggered_price'],
                'threshold_price': row['threshold_price'],
                'direction': row['direction'],
                'ai_analysis': ai_analysis,
                'user_email': row['user_email'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        logger.info(f"查询到 {len(results)} 条告警日志")
        
        return results
        
    except Exception as e:
        logger.error(f"查询告警日志失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_alert_logs_count(
    user_email: Optional[str] = None,
    stock_code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """
    获取告警日志总数（用于分页）
    
    参数: 同 get_alert_logs
    
    返回:
    int: 告警日志总数
    """
    try:
        # 确保数据库已初始化
        init_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 构建查询语句
        query = 'SELECT COUNT(*) FROM alert_logs WHERE 1=1'
        params = []
        
        # 添加过滤条件
        if user_email:
            query += ' AND user_email = ?'
            params.append(user_email)
        
        if stock_code:
            query += ' AND stock_code = ?'
            params.append(stock_code)
        
        if start_date:
            query += ' AND alert_timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND alert_timestamp <= ?'
            params.append(end_date)
        
        # 执行查询
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        return count
        
    except Exception as e:
        logger.error(f"查询告警日志总数失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def cleanup_old_alerts(days: int = 30) -> int:
    """
    清理旧的告警日志
    
    参数:
    days (int): 保留多少天的日志
    
    返回:
    int: 删除的记录数
    """
    try:
        # 确保数据库已初始化
        init_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 计算删除时间点
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 删除旧记录
        cursor.execute('''
            DELETE FROM alert_logs 
            WHERE alert_timestamp < ?
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        
        # 提交更改
        conn.commit()
        
        logger.info(f"清理了 {deleted_count} 条超过 {days} 天的告警日志")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理告警日志失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close() 