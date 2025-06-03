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
                ai_configurations_json_encrypted TEXT,
                proxy_settings_json_encrypted TEXT,
                preferred_llm TEXT DEFAULT 'openai',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查是否需要添加新字段（用于数据库升级）
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'preferred_llm' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN preferred_llm TEXT DEFAULT "openai"')
            logger.info("已添加preferred_llm字段到用户表")
        
        if 'ai_configurations_json_encrypted' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN ai_configurations_json_encrypted TEXT')
            logger.info("已添加ai_configurations_json_encrypted字段到用户表")
        
        if 'proxy_settings_json_encrypted' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN proxy_settings_json_encrypted TEXT')
            logger.info("已添加proxy_settings_json_encrypted字段到用户表")
        
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
        # 连接数据库，确保读取最新数据
        conn = sqlite3.connect(DB_PATH)
        # 设置WAL模式并确保读取最新数据
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=FULL')
        # 确保读取到最新提交的数据
        conn.execute('BEGIN IMMEDIATE')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        logger.info(f"开始获取用户配置: user_id={user_id}")
        
        # 查找用户配置
        cursor.execute('''
            SELECT tushare_token, email_sender_address, email_smtp_server, 
                   email_smtp_port, email_smtp_user, email_smtp_password_encrypted,
                   ai_api_keys_json_encrypted, ai_configurations_json_encrypted,
                   proxy_settings_json_encrypted, preferred_llm, updated_at
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        config_row = cursor.fetchone()
        if not config_row:
            logger.warning(f"未找到用户配置: user_id={user_id}")
            return None
        
        logger.info(f"找到用户配置: user_id={user_id}, 最后更新={config_row['updated_at']}")
        
        # 解密敏感信息
        email_password = None
        if config_row['email_smtp_password_encrypted']:
            email_password = decrypt_string(config_row['email_smtp_password_encrypted'])
        
        ai_api_keys = {}
        if config_row['ai_api_keys_json_encrypted']:
            ai_api_keys = decrypt_json(config_row['ai_api_keys_json_encrypted']) or {}
        
        ai_configurations = {}
        if config_row['ai_configurations_json_encrypted']:
            try:
                ai_configurations = decrypt_json(config_row['ai_configurations_json_encrypted']) or {}
                logger.info(f"AI配置解密成功: user_id={user_id}, 提供商数量={len(ai_configurations)}")
                
                # 详细记录每个提供商的配置状态
                for provider_id, provider_config in ai_configurations.items():
                    has_api_key = bool(provider_config.get('api_key'))
                    model = provider_config.get('model_id', 'N/A')
                    enabled = provider_config.get('enabled', False)
                    logger.info(f"  提供商 {provider_id}: 模型={model}, 启用={enabled}, 有密钥={has_api_key}")
                    
            except Exception as e:
                logger.error(f"AI配置解密失败: user_id={user_id}, 错误={e}")
                ai_configurations = {}
        
        proxy_settings = {}
        if config_row['proxy_settings_json_encrypted']:
            try:
                proxy_settings = decrypt_json(config_row['proxy_settings_json_encrypted']) or {}
                if proxy_settings:
                    proxy_enabled = proxy_settings.get('enabled', False)
                    proxy_host = proxy_settings.get('host', 'N/A')
                    logger.info(f"代理设置: user_id={user_id}, 启用={proxy_enabled}, 主机={proxy_host}")
            except Exception as e:
                logger.error(f"代理设置解密失败: user_id={user_id}, 错误={e}")
                proxy_settings = {}
        
        # 提交事务
        conn.commit()
        
        user_config = {
            'tushare_token': config_row['tushare_token'],
            'email_sender_address': config_row['email_sender_address'],
            'email_smtp_server': config_row['email_smtp_server'],
            'email_smtp_port': config_row['email_smtp_port'],
            'email_smtp_user': config_row['email_smtp_user'],
            'email_smtp_password': email_password,
            'ai_api_keys': ai_api_keys,
            'ai_configurations': ai_configurations,
            'proxy_settings': proxy_settings,
            'preferred_llm': config_row['preferred_llm'] or 'openai'
        }
        
        logger.info(f"用户配置获取成功: user_id={user_id}")
        return user_config
        
    except Exception as e:
        logger.error(f"获取用户配置失败: user_id={user_id}, 错误={e}")
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
                   ai_api_keys_json_encrypted, ai_configurations_json_encrypted,
                   proxy_settings_json_encrypted, preferred_llm
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        config_row = cursor.fetchone()
        if not config_row:
            return None
        
        # 检查AI API Keys
        ai_keys_count = 0
        ai_keys_detail = {}
        if config_row['ai_api_keys_json_encrypted']:
            ai_api_keys = decrypt_json(config_row['ai_api_keys_json_encrypted'])
            if ai_api_keys:
                ai_keys_count = len(ai_api_keys)
                # 提供可用的LLM列表（不暴露API密钥）
                ai_keys_detail = {key: bool(value) for key, value in ai_api_keys.items()}
        
        # 检查AI配置
        ai_configurations_count = 0
        ai_providers_configured = []
        if config_row['ai_configurations_json_encrypted']:
            ai_configurations = decrypt_json(config_row['ai_configurations_json_encrypted'])
            if ai_configurations:
                ai_configurations_count = len(ai_configurations)
                ai_providers_configured = list(ai_configurations.keys())
        
        # 检查代理设置
        has_proxy_config = False
        proxy_enabled = False
        if config_row['proxy_settings_json_encrypted']:
            proxy_settings = decrypt_json(config_row['proxy_settings_json_encrypted'])
            if proxy_settings:
                has_proxy_config = bool(proxy_settings.get('host') and proxy_settings.get('port'))
                proxy_enabled = proxy_settings.get('enabled', False)
        
        return {
            'has_tushare_token': bool(config_row['tushare_token']),
            'has_email_config': bool(config_row['email_smtp_server'] and config_row['email_smtp_user']),
            'email_sender_address': config_row['email_sender_address'],
            'email_smtp_server': config_row['email_smtp_server'],
            'email_smtp_port': config_row['email_smtp_port'],
            'email_smtp_user': config_row['email_smtp_user'],
            'has_email_password': bool(config_row['email_smtp_password_encrypted']),
            'ai_keys_count': ai_keys_count,
            'ai_keys_detail': ai_keys_detail,
            'ai_configurations_count': ai_configurations_count,
            'ai_providers_configured': ai_providers_configured,
            'has_proxy_config': has_proxy_config,
            'proxy_enabled': proxy_enabled,
            'preferred_llm': config_row['preferred_llm'] or 'openai'
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
        # 连接数据库，确保使用正确的同步模式
        conn = sqlite3.connect(DB_PATH)
        # 设置WAL模式以提高并发性能，但确保读写一致性
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=FULL')  # 确保数据完全同步到磁盘
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
        
        if 'ai_configurations' in config_data:
            encrypted_configs = encrypt_json(config_data['ai_configurations'])
            update_fields.append('ai_configurations_json_encrypted = ?')
            update_values.append(encrypted_configs)
            logger.info(f"准备更新AI配置: user_id={user_id}, 配置数量={len(config_data['ai_configurations'])}")
        
        if 'proxy_settings' in config_data:
            encrypted_proxy = encrypt_json(config_data['proxy_settings'])
            update_fields.append('proxy_settings_json_encrypted = ?')
            update_values.append(encrypted_proxy)
        
        if 'preferred_llm' in config_data:
            # 验证LLM选择是否有效
            valid_llms = ['openai', 'gemini', 'deepseek']
            preferred_llm = config_data['preferred_llm'].lower() if config_data['preferred_llm'] else 'openai'
            if preferred_llm not in valid_llms:
                preferred_llm = 'openai'
            update_fields.append('preferred_llm = ?')
            update_values.append(preferred_llm)
        
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
        
        # 强制提交更改并等待写入完成
        conn.commit()
        
        # 添加验证步骤：立即读取更新后的配置验证是否成功
        if cursor.rowcount > 0:
            # 等待一小段时间确保数据库完全同步
            import time
            time.sleep(0.1)
            
            # 验证更新是否生效
            verification_success = False
            try:
                # 重新连接数据库进行验证
                verify_conn = sqlite3.connect(DB_PATH)
                verify_conn.row_factory = sqlite3.Row
                verify_cursor = verify_conn.cursor()
                
                verify_cursor.execute('''
                    SELECT updated_at, ai_configurations_json_encrypted 
                    FROM users 
                    WHERE id = ? AND is_active = 1
                ''', (user_id,))
                
                verify_row = verify_cursor.fetchone()
                if verify_row:
                    # 检查时间戳是否为最新
                    stored_time = datetime.fromisoformat(verify_row['updated_at'].replace('Z', ''))
                    time_diff = abs((datetime.now() - stored_time).total_seconds())
                    
                    if time_diff < 2:  # 2秒内的更新认为是有效的
                        verification_success = True
                        logger.info(f"配置更新验证成功: user_id={user_id}, 时间差={time_diff:.2f}秒")
                    else:
                        logger.warning(f"配置更新时间异常: user_id={user_id}, 时间差={time_diff:.2f}秒")
                
                verify_conn.close()
                
            except Exception as e:
                logger.error(f"配置更新验证失败: {e}")
            
            if verification_success:
                logger.info(f"用户配置更新并验证成功: user_id={user_id}")
                return True, "配置更新成功"
            else:
                logger.warning(f"用户配置更新成功但验证失败: user_id={user_id}")
                return True, "配置更新成功（验证警告）"
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

def get_user_config_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    根据用户邮箱获取用户配置
    
    参数:
    email (str): 用户邮箱
    
    返回:
    dict: 用户配置信息，如果用户不存在返回None
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 根据邮箱查找用户ID
        cursor.execute('''
            SELECT id FROM users 
            WHERE email = ? AND is_active = 1
        ''', (email,))
        
        user_row = cursor.fetchone()
        if not user_row:
            return None
        
        user_id = user_row['id']
        
        # 获取用户配置
        return get_user_config(user_id)
        
    except Exception as e:
        logger.error(f"根据邮箱获取用户配置失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_config_for_editing(user_id: int) -> Optional[Dict[str, Any]]:
    """
    获取用户的详细配置信息用于编辑（部分敏感信息会被掩码）
    
    参数:
    user_id (int): 用户ID
    
    返回:
    dict: 用户配置信息，敏感信息被掩码处理
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
                   ai_api_keys_json_encrypted, ai_configurations_json_encrypted,
                   proxy_settings_json_encrypted, preferred_llm
            FROM users 
            WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        config_row = cursor.fetchone()
        if not config_row:
            return None
        
        # 解密和处理配置信息
        ai_api_keys = {}
        if config_row['ai_api_keys_json_encrypted']:
            ai_api_keys = decrypt_json(config_row['ai_api_keys_json_encrypted']) or {}
        
        ai_configurations = {}
        if config_row['ai_configurations_json_encrypted']:
            ai_configurations = decrypt_json(config_row['ai_configurations_json_encrypted']) or {}
        
        proxy_settings = {}
        if config_row['proxy_settings_json_encrypted']:
            proxy_settings = decrypt_json(config_row['proxy_settings_json_encrypted']) or {}
        
        # 处理敏感信息的显示
        def mask_sensitive_value(value):
            """对敏感信息进行掩码处理"""
            if not value:
                return ''
            if len(value) <= 8:
                return '*' * len(value)
            return value[:4] + '*' * (len(value) - 8) + value[-4:]
        
        # 处理AI配置中的API密钥
        masked_ai_configurations = {}
        for provider_id, config in ai_configurations.items():
            masked_config = config.copy()
            if 'api_key' in masked_config and masked_config['api_key']:
                masked_config['api_key'] = mask_sensitive_value(masked_config['api_key'])
            masked_ai_configurations[provider_id] = masked_config
        
        # 处理代理设置中的密码
        masked_proxy_settings = proxy_settings.copy()
        if 'password' in masked_proxy_settings and masked_proxy_settings['password']:
            masked_proxy_settings['password'] = mask_sensitive_value(masked_proxy_settings['password'])
        
        return {
            'tushare_token': mask_sensitive_value(config_row['tushare_token']) if config_row['tushare_token'] else '',
            'email_sender_address': config_row['email_sender_address'] or '',
            'email_smtp_server': config_row['email_smtp_server'] or '',
            'email_smtp_port': config_row['email_smtp_port'] or 587,
            'email_smtp_user': config_row['email_smtp_user'] or '',
            'has_email_password': bool(config_row['email_smtp_password_encrypted']),
            'ai_api_keys': {k: mask_sensitive_value(v) for k, v in ai_api_keys.items() if v},
            'ai_configurations': masked_ai_configurations,
            'proxy_settings': masked_proxy_settings,
            'preferred_llm': config_row['preferred_llm'] or 'openai'
        }
        
    except Exception as e:
        logger.error(f"获取用户编辑配置失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close() 