import os
import logging
import requests
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger('ai_analysis_service')

# 全局AI API配置（作为后备配置）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

def get_basic_ai_analysis(stock_code, current_price, breakout_direction, user_config: Optional[Dict[str, Any]] = None):
    """
    获取股票的基本AI分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向 ('UP' 或 'DOWN')
    user_config (dict, optional): 用户配置，包含AI API密钥
    
    返回:
    str: AI生成的分析文本
    """
    # 获取用户配置的AI API密钥
    ai_api_keys = {}
    if user_config and user_config.get('ai_api_keys'):
        ai_api_keys = user_config['ai_api_keys']
    
    # 优先尝试使用用户配置的OpenAI密钥
    openai_key = ai_api_keys.get('openai', OPENAI_API_KEY)
    
    if openai_key:
        try:
            result = get_analysis_with_openai(stock_code, current_price, breakout_direction, openai_key)
            if not result.startswith("AI分析") and "失败" not in result and "错误" not in result:
                return result
        except Exception as e:
            logger.warning(f"OpenAI分析失败，尝试其他模型: {e}")
    
    # 如果OpenAI失败，尝试使用Gemini
    gemini_key = ai_api_keys.get('gemini', os.getenv('GEMINI_API_KEY', ''))
    if gemini_key:
        try:
            result = get_analysis_with_gemini(stock_code, current_price, breakout_direction, gemini_key)
            if not result.startswith("AI分析") and "失败" not in result and "错误" not in result:
                return result
        except Exception as e:
            logger.warning(f"Gemini分析失败，尝试其他模型: {e}")
    
    # 如果都失败，尝试DeepSeek
    deepseek_key = ai_api_keys.get('deepseek', os.getenv('DEEPSEEK_API_KEY', ''))
    if deepseek_key:
        try:
            result = get_analysis_with_deepseek(stock_code, current_price, breakout_direction, deepseek_key)
            if not result.startswith("AI分析") and "失败" not in result and "错误" not in result:
                return result
        except Exception as e:
            logger.warning(f"DeepSeek分析失败: {e}")
    
    logger.error("所有AI分析服务都不可用")
    return "AI分析功能暂不可用（未配置有效的API密钥）"

def get_analysis_with_openai(stock_code, current_price, breakout_direction, api_key):
    """
    使用OpenAI API获取股票分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向
    api_key (str): OpenAI API密钥
    
    返回:
    str: AI分析结果
    """
    if not api_key:
        return "OpenAI API密钥未配置"
    
    # 构建提示词
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    prompt = f"股票{stock_code}当前价格{current_price}，已{direction_text}突破阈值，请基于此信息给出一个非常简短的初步观察或建议，限制在50字以内。"
    
    try:
        # 构建API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长简洁明了地分析A股市场。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # 发送请求
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content'].strip()
            logger.info(f"成功获取OpenAI分析: {analysis}")
            return analysis
        else:
            logger.error(f"OpenAI API请求失败: {response.status_code} {response.text}")
            return f"OpenAI分析请求失败（HTTP {response.status_code}）"
            
    except Exception as e:
        logger.error(f"获取OpenAI分析时出错: {e}")
        return "OpenAI分析过程中发生错误"

def get_analysis_with_gemini(stock_code, current_price, breakout_direction, api_key):
    """
    使用Google Gemini API获取股票分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向
    api_key (str): Gemini API密钥
    
    返回:
    str: AI分析结果
    """
    if not api_key:
        return "Gemini API密钥未配置"
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    prompt = f"股票{stock_code}当前价格{current_price}，已{direction_text}突破阈值，请基于此信息给出一个非常简短的初步观察或建议，限制在50字以内。"
    
    try:
        # 构建API请求
        url = f"{GEMINI_API_URL}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            analysis = result['candidates'][0]['content']['parts'][0]['text'].strip()
            logger.info(f"成功获取Gemini AI分析: {analysis}")
            return analysis
        else:
            logger.error(f"Gemini API请求失败: {response.status_code} {response.text}")
            return f"Gemini分析请求失败（HTTP {response.status_code}）"
            
    except Exception as e:
        logger.error(f"获取Gemini AI分析时出错: {e}")
        return "Gemini分析过程中发生错误"

def get_analysis_with_deepseek(stock_code, current_price, breakout_direction, api_key):
    """
    使用DeepSeek API获取股票分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向
    api_key (str): DeepSeek API密钥
    
    返回:
    str: AI分析结果
    """
    if not api_key:
        return "DeepSeek API密钥未配置"
    
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    prompt = f"股票{stock_code}当前价格{current_price}，已{direction_text}突破阈值，请基于此信息给出一个非常简短的初步观察或建议，限制在50字以内。"
    
    try:
        # 构建API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长简洁明了地分析A股市场。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # 发送请求
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content'].strip()
            logger.info(f"成功获取DeepSeek分析: {analysis}")
            return analysis
        else:
            logger.error(f"DeepSeek API请求失败: {response.status_code} {response.text}")
            return f"DeepSeek分析请求失败（HTTP {response.status_code}）"
            
    except Exception as e:
        logger.error(f"获取DeepSeek AI分析时出错: {e}")
        return "DeepSeek分析过程中发生错误" 