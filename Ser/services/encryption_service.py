"""
加密服务模块
用于处理敏感信息（如邮件密码、AI API密钥）的加密和解密
"""

import os
import json
import base64
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger('encryption_service')

# 全局加密器实例
_cipher_suite = None

def _get_encryption_key() -> bytes:
    """
    获取加密密钥
    
    使用固定的主密钥生成加密密钥
    """
    # 使用固定的主密钥（与项目其他部分保持一致，使用数据库而非环境变量）
    master_key = 'fintech-ai-encryption-master-key-2024-secure'
    
    # 使用PBKDF2从主密钥派生加密密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'stock-monitor-salt',  # 在生产环境中应该使用随机盐
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    return key

def _get_cipher():
    """获取加密器实例"""
    global _cipher_suite
    if _cipher_suite is None:
        key = _get_encryption_key()
        _cipher_suite = Fernet(key)
    return _cipher_suite

def encrypt_string(plaintext: str) -> Optional[str]:
    """
    加密字符串
    
    参数:
    plaintext (str): 要加密的明文字符串
    
    返回:
    str: 加密后的base64字符串，如果加密失败返回None
    """
    if not plaintext:
        return None
    
    try:
        cipher = _get_cipher()
        encrypted_data = cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"加密字符串失败: {e}")
        return None

def decrypt_string(encrypted_text: str) -> Optional[str]:
    """
    解密字符串
    
    参数:
    encrypted_text (str): 要解密的base64加密字符串
    
    返回:
    str: 解密后的明文字符串，如果解密失败返回None
    """
    if not encrypted_text:
        return None
    
    try:
        cipher = _get_cipher()
        encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"解密字符串失败: {e}")
        return None

def encrypt_json(data: Dict[str, Any]) -> Optional[str]:
    """
    加密JSON数据
    
    参数:
    data (dict): 要加密的字典数据
    
    返回:
    str: 加密后的base64字符串，如果加密失败返回None
    """
    if not data:
        return None
    
    try:
        json_string = json.dumps(data, ensure_ascii=False)
        return encrypt_string(json_string)
    except Exception as e:
        logger.error(f"加密JSON数据失败: {e}")
        return None

def decrypt_json(encrypted_text: str) -> Optional[Dict[str, Any]]:
    """
    解密JSON数据
    
    参数:
    encrypted_text (str): 要解密的base64加密字符串
    
    返回:
    dict: 解密后的字典数据，如果解密失败返回None
    """
    if not encrypted_text:
        return None
    
    try:
        json_string = decrypt_string(encrypted_text)
        if json_string:
            return json.loads(json_string)
        return None
    except Exception as e:
        logger.error(f"解密JSON数据失败: {e}")
        return None

def generate_new_key() -> str:
    """
    生成新的加密密钥
    
    返回:
    str: 新的base64编码的密钥
    """
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()

# 测试函数
if __name__ == "__main__":
    # 测试加密解密功能
    test_string = "test_password_123"
    encrypted = encrypt_string(test_string)
    decrypted = decrypt_string(encrypted)
    
    print(f"原文: {test_string}")
    print(f"加密: {encrypted}")
    print(f"解密: {decrypted}")
    print(f"加密解密成功: {test_string == decrypted}")
    
    # 测试JSON加密解密
    test_json = {"openai": "sk-test123", "gemini": "test-api-key"}
    encrypted_json = encrypt_json(test_json)
    decrypted_json = decrypt_json(encrypted_json)
    
    print(f"原JSON: {test_json}")
    print(f"加密JSON: {encrypted_json}")
    print(f"解密JSON: {decrypted_json}")
    print(f"JSON加密解密成功: {test_json == decrypted_json}") 