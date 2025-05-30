import os
import logging
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger('ai_analysis_service')

# OpenAI API配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

def get_basic_ai_analysis(stock_code, current_price, breakout_direction):
    """
    获取股票的基本AI分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向 ('UP' 或 'DOWN')
    
    返回:
    str: AI生成的分析文本
    """
    if not OPENAI_API_KEY:
        logger.error("未设置OPENAI_API_KEY环境变量，无法进行AI分析")
        return "AI分析功能暂不可用（API密钥未配置）"
    
    # 构建提示词
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    prompt = f"股票{stock_code}当前价格{current_price}，已{direction_text}突破阈值，请基于此信息给出一个非常简短的初步观察或建议，限制在50字以内。"
    
    try:
        # 构建API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
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
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content'].strip()
            logger.info(f"成功获取AI分析: {analysis}")
            return analysis
        else:
            logger.error(f"API请求失败: {response.status_code} {response.text}")
            return f"AI分析请求失败（HTTP {response.status_code}）"
            
    except Exception as e:
        logger.error(f"获取AI分析时出错: {e}")
        return "AI分析过程中发生错误，请稍后再试"

# 备用函数：使用Gemini API
def get_analysis_with_gemini(stock_code, current_price, breakout_direction):
    """
    使用Google Gemini API获取股票分析
    
    参数与get_basic_ai_analysis相同
    """
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    if not GEMINI_API_KEY:
        logger.error("未设置GEMINI_API_KEY环境变量，无法进行AI分析")
        return "AI分析功能暂不可用（API密钥未配置）"
    
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    prompt = f"股票{stock_code}当前价格{current_price}，已{direction_text}突破阈值，请基于此信息给出一个非常简短的初步观察或建议，限制在50字以内。"
    
    try:
        # 构建API请求
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
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
        response = requests.post(url, headers=headers, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            analysis = result['candidates'][0]['content']['parts'][0]['text'].strip()
            logger.info(f"成功获取Gemini AI分析: {analysis}")
            return analysis
        else:
            logger.error(f"Gemini API请求失败: {response.status_code} {response.text}")
            return f"AI分析请求失败（HTTP {response.status_code}）"
            
    except Exception as e:
        logger.error(f"获取Gemini AI分析时出错: {e}")
        return "AI分析过程中发生错误，请稍后再试" 