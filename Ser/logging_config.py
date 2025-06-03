#!/usr/bin/env python3
"""
日志配置模块 - 处理Windows控制台编码问题
"""

import logging
import sys
import os

def setup_logging():
    """配置日志处理器，解决Windows控制台编码问题"""
    
    # 创建自定义的日志格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 文件处理器（UTF-8编码）
    try:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"无法创建文件日志处理器: {e}")
    
    # 控制台处理器（处理编码问题）
    try:
        # 在Windows上使用特殊处理
        if sys.platform.startswith('win'):
            # 尝试设置控制台编码为UTF-8
            try:
                import locale
                import codecs
                
                # 获取系统默认编码
                encoding = locale.getpreferredencoding()
                
                # 创建一个安全的流写入器
                class SafeStreamHandler(logging.StreamHandler):
                    def emit(self, record):
                        try:
                            msg = self.format(record)
                            # 将特殊Unicode字符替换为ASCII兼容字符
                            safe_msg = msg.replace('✓', '[OK]').replace('✗', '[FAIL]').replace('⚠', '[WARN]').replace('🔍', '[SEARCH]').replace('📊', '[DATA]').replace('📈', '[STOCK]').replace('🤖', '[AI]').replace('🔄', '[PROC]').replace('🧪', '[TEST]').replace('✅', '[DONE]')
                            
                            stream = self.stream
                            stream.write(safe_msg + self.terminator)
                            self.flush()
                        except Exception:
                            self.handleError(record)
                
                console_handler = SafeStreamHandler()
                
            except Exception:
                # 回退到标准处理器
                console_handler = logging.StreamHandler()
        else:
            # 非Windows系统使用标准处理器
            console_handler = logging.StreamHandler()
        
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
    except Exception as e:
        print(f"无法创建控制台日志处理器: {e}")
    
    return root_logger

def get_logger(name):
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

# 自动初始化日志配置
setup_logging() 