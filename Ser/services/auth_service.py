"""
用户认证服务模块
用于处理用户注册、登录、密码验证等功能
"""

import sqlite3
import os
import logging
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .encryption_service import encrypt_string, decrypt_string, encrypt_json, decrypt_json

logger = logging.getLogger('auth_service')

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stock_monitor.db')

def init_user_database():
    """
    初始化用户数据库表
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
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email)
        ''')
        
        # 提交更改
        conn.commit()
        
        logger.info("用户数据库表初始化成功")
        
    except Exception as e:
        logger.error(f"用户数据库表初始化失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    注册新用户
    
    参数:
    username (str): 用户名
    email (str): 邮箱
    password (str): 密码
    
    返回:
    tuple: (成功标志, 消息)
    """
    try:
        # 确保数据库已初始化
        init_user_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return False, "用户名已存在"
        
        # 检查邮箱是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return False, "邮箱已被注册"
        
        # 生成密码哈希
        password_hash = generate_password_hash(password)
        
        # 插入新用户
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        # 提交更改
        conn.commit()
        
        logger.info(f"用户注册成功: {username} ({email})")
        return True, "注册成功"
        
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        return False, "注册失败，请稍后重试"
    finally:
        if 'conn' in locals():
            conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    验证用户登录
    
    参数:
    username (str): 用户名或邮箱
    password (str): 密码
    
    返回:
    dict: 用户信息（不包含密码），如果验证失败返回None
    """
    try:
        # 确保数据库已初始化
        init_user_database()
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查找用户（支持用户名或邮箱登录）
        cursor.execute('''
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username, username))
        
        user_row = cursor.fetchone()
        if not user_row:
            return None
        
        # 验证密码
        if not check_password_hash(user_row['password_hash'], password):
            return None
        
        # 返回用户信息（不包含密码哈希）
        user_info = {
            'id': user_row['id'],
            'username': user_row['username'],
            'email': user_row['email'],
            'created_at': user_row['created_at'],
            'updated_at': user_row['updated_at']
        }
        
        logger.info(f"用户登录成功: {username}")
        return user_info
        
    except Exception as e:
        logger.error(f"用户验证失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    根据用户ID获取用户信息
    
    参数:
    user_id (int): 用户ID
    
    返回:
    dict: 用户信息，如果用户不存在返回None
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查找用户
        cursor.execute('''
            SELECT id, username, email, created_at, updated_at
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        user_row = cursor.fetchone()
        if not user_row:
            return None
        
        return dict(user_row)
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_config(user_id: int) -> Optional[Dict[str, Any]]:
    """
    获取用户的配置信息
    
    参数:
    user_id (int): 用户ID
    
    返回:
    dict: 用户配置信息，包含解密后的敏感信息
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查找用户配置
        cursor.execute('''
            SELECT tushare_token, email_sender_address, email_smtp_server, 
                   email_smtp_port, email_smtp_user, email_smtp_password_encrypted,
                   ai_api_keys_json_encrypted
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        config_row = cursor.fetchone()
        if not config_row:
            return None
        
        # 解密敏感信息
        email_password = None
        if config_row['email_smtp_password_encrypted']:
            email_password = decrypt_string(config_row['email_smtp_password_encrypted'])
        
        ai_api_keys = {}
        if config_row['ai_api_keys_json_encrypted']:
            ai_api_keys = decrypt_json(config_row['ai_api_keys_json_encrypted']) or {}
        
        return {
            'tushare_token': config_row['tushare_token'],
            'email_sender_address': config_row['email_sender_address'],
            'email_smtp_server': config_row['email_smtp_server'],
            'email_smtp_port': config_row['email_smtp_port'],
            'email_smtp_user': config_row['email_smtp_user'],
            'email_smtp_password': email_password,
            'ai_api_keys': ai_api_keys
        }
        
    except Exception as e:
        logger.error(f"获取用户配置失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_config_summary(user_id: int) -> Optional[Dict[str, Any]]:
    """
    获取用户配置的摘要信息（不包含敏感数据）
    
    参数:
    user_id (int): 用户ID
    
    返回:
    dict: 用户配置摘要，只包含是否已配置的状态
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查找用户配置
        cursor.execute('''
            SELECT tushare_token, email_sender_address, email_smtp_server, 
                   email_smtp_port, email_smtp_user, email_smtp_password_encrypted,
                   ai_api_keys_json_encrypted
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        config_row = cursor.fetchone()
        if not config_row:
            return None
        
        # 检查AI API Keys
        ai_keys_count = 0
        if config_row['ai_api_keys_json_encrypted']:
            ai_api_keys = decrypt_json(config_row['ai_api_keys_json_encrypted'])
            if ai_api_keys:
                ai_keys_count = len(ai_api_keys)
        
        return {
            'has_tushare_token': bool(config_row['tushare_token']),
            'has_email_config': bool(config_row['email_smtp_server'] and config_row['email_smtp_user']),
            'email_sender_address': config_row['email_sender_address'],
            'email_smtp_server': config_row['email_smtp_server'],
            'email_smtp_port': config_row['email_smtp_port'],
            'email_smtp_user': config_row['email_smtp_user'],
            'has_email_password': bool(config_row['email_smtp_password_encrypted']),
            'ai_keys_count': ai_keys_count
        }
        
    except Exception as e:
        logger.error(f"获取用户配置摘要失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def update_user_config(user_id: int, config_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    更新用户配置
    
    参数:
    user_id (int): 用户ID
    config_data (dict): 配置数据
    
    返回:
    tuple: (成功标志, 消息)
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 准备更新的字段和值
        update_fields = []
        update_values = []
        
        # 处理各个配置字段
        if 'tushare_token' in config_data:
            update_fields.append('tushare_token = ?')
            update_values.append(config_data['tushare_token'])
        
        if 'email_sender_address' in config_data:
            update_fields.append('email_sender_address = ?')
            update_values.append(config_data['email_sender_address'])
        
        if 'email_smtp_server' in config_data:
            update_fields.append('email_smtp_server = ?')
            update_values.append(config_data['email_smtp_server'])
        
        if 'email_smtp_port' in config_data:
            update_fields.append('email_smtp_port = ?')
            update_values.append(config_data['email_smtp_port'])
        
        if 'email_smtp_user' in config_data:
            update_fields.append('email_smtp_user = ?')
            update_values.append(config_data['email_smtp_user'])
        
        # 处理加密字段
        if 'email_smtp_password' in config_data:
            encrypted_password = encrypt_string(config_data['email_smtp_password'])
            update_fields.append('email_smtp_password_encrypted = ?')
            update_values.append(encrypted_password)
        
        if 'ai_api_keys' in config_data:
            encrypted_keys = encrypt_json(config_data['ai_api_keys'])
            update_fields.append('ai_api_keys_json_encrypted = ?')
            update_values.append(encrypted_keys)
        
        if not update_fields:
            return False, "没有需要更新的配置"
        
        # 添加更新时间
        update_fields.append('updated_at = ?')
        update_values.append(datetime.now())
        
        # 添加用户ID作为WHERE条件
        update_values.append(user_id)
        
        # 执行更新
        sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, update_values)
        
        # 提交更改
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"用户配置更新成功: user_id={user_id}")
            return True, "配置更新成功"
        else:
            return False, "用户不存在"
        
    except Exception as e:
        logger.error(f"用户配置更新失败: {e}")
        return False, "配置更新失败，请稍后重试"
    finally:
        if 'conn' in locals():
            conn.close()

def change_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    """
    修改用户密码
    
    参数:
    user_id (int): 用户ID
    old_password (str): 旧密码
    new_password (str): 新密码
    
    返回:
    tuple: (成功标志, 消息)
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取当前密码哈希
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return False, "用户不存在"
        
        # 验证旧密码
        if not check_password_hash(user_row['password_hash'], old_password):
            return False, "当前密码错误"
        
        # 生成新密码哈希
        new_password_hash = generate_password_hash(new_password)
        
        # 更新密码
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = ? 
            WHERE id = ?
        ''', (new_password_hash, datetime.now(), user_id))
        
        # 提交更改
        conn.commit()
        
        logger.info(f"用户密码修改成功: user_id={user_id}")
        return True, "密码修改成功"
        
    except Exception as e:
        logger.error(f"用户密码修改失败: {e}")
        return False, "密码修改失败，请稍后重试"
    finally:
        if 'conn' in locals():
            conn.close() 